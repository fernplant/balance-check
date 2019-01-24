import sys
import requests
from bs4 import BeautifulSoup
from balance_check import logger, captcha_solver, config
from balance_check.providers import BalanceCheckProvider
from balance_check.validators.credit_card import Issuer, CreditCardSchema


class Simon(BalanceCheckProvider):
    def __init__(self):
        super().__init__()

        self.website_url = "https://www.simon.com/giftcard/card_balance.aspx"
        self.schema = CreditCardSchema([Issuer.Visa])

    def scrape(self, fields):
        session = requests.Session()
        session.headers.update({"User-Agent": config.USER_AGENT})

        logger.info("Fetching balance check page")
        resp = session.get(self.website_url)
        if resp.status_code != 200:
            logger.critical(
                f"Failed to GET Simon website (status code {resp.status_code})"
            )
            sys.exit(1)

        page_html = BeautifulSoup(resp.content, features="html.parser")

        recaptcha_field = page_html.find("div", class_="g-recaptcha")
        if not recaptcha_field:
            logger.critical("Unable to find reCAPTCHA")
            sys.exit(1)

        site_key = recaptcha_field["data-sitekey"]

        logger.info("Solving reCAPTCHA (~30s)")
        captcha = captcha_solver.solve_recaptcha(self.website_url, site_key)
        if captcha["errorId"] != 0:
            logger.critical(
                f"Unable to solve reCAPTCHA ({captcha['errorDescription']})"
            )
            sys.exit(1)

        # These fields are present on balance check page, request blocked if not included
        fields["__EVENTTARGET"] = ""
        fields["__EVENTARGUMENT"] = ""
        fields["__LASTFOCUS"] = ""
        fields["__VIEWSTATE"] = page_html.find("input", id="__VIEWSTATE")["value"]
        fields["__VIEWSTATEGENERATOR"] = page_html.find(
            "input", id="__VIEWSTATEGENERATOR"
        )["value"]
        fields["__VIEWSTATEENCRYPTED"] = ""
        fields["__EVENTVALIDATION"] = page_html.find("input", id="__EVENTVALIDATION")[
            "value"
        ]
        fields["ctl00$ctl00$header1$EmailLogin"] = ""
        fields["ctl00$ctl00$header1$PasswordLogin"] = ""
        fields[
            "ctl00$ctl00$FullContent$MainContent$checkBalanceSubmit"
        ] = "CHECK YOUR BALANCE"

        fields["g-recaptcha-response"] = captcha["solution"]["gRecaptchaResponse"]

        session.headers.update(
            {
                "User-Agent": config.USER_AGENT,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "en-US,en;q=0.9",
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "application/x-www-form-urlencoded",
                "Referer": self.website_url,
                "origin": "https://www.simon.com",
            }
        )

        logger.info("Fetching card balance")
        form_resp = session.post(self.website_url, data=fields)
        if form_resp.status_code != 200:
            logger.critical(
                f"Failed to retrieve card balance (status code {form_resp.status_code})"
            )
            sys.exit(1)

        balance_html = BeautifulSoup(form_resp.content, features="html.parser")

        if balance_html.find("label", text="CAPTCHA: Please validate"):
            raise RuntimeError("Invalid CAPTCHA answer supplied.")

        try:
            avail_balance = balance_html.find(
                id="ctl00_ctl00_FullContent_MainContent_lblBalance"
            ).text
            initial_balance = balance_html.find_all(
                "td", _class="tblinfo"
            )  # [-1].text.strip()
            print(initial_balance)
        except:
            print("DUMP:", resp.text)
            raise RuntimeError("Could not find balance on page")

        logger.info(f"Success! Card balance: {avail_balance}")

        return {"initial_balance": initial_balance, "available_balance": avail_balance}

    def check_balance(self, **kwargs):
        if self.validate(kwargs):
            logger.info(
                "Checking balance for card: {}, exp {}/{}".format(
                    kwargs["card_number"], kwargs["exp_month"], kwargs["exp_year"]
                )
            )

            return self.scrape(
                {
                    "ctl00$ctl00$FullContent$MainContent$tbNumber": kwargs[
                        "card_number"
                    ],
                    "ctl00$ctl00$FullContent$MainContent$tbExpDate": kwargs["exp_month"]
                    + kwargs["exp_year"],
                    "ctl00$ctl00$FullContent$MainContent$tbCid": kwargs["cvv"],
                }
            )
