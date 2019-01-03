import requests
import time
from balance_check import logger, captcha_solver, config
from balance_check.providers import BalanceCheckProvider
from balance_check.validators.gift_card import Merchant, GiftCardSchema


class BestBuy(BalanceCheckProvider):
    def __init__(self):
        super().__init__()

        self.website_url = "https://www.bestbuy.com/gift-card-balance/api/lookup"
        self.schema = GiftCardSchema(Merchant.BestBuy)

    def scrape(self, **kwargs):
        session = requests.Session()
        session.headers.update(
            {
                "User-Agent": config.USER_AGENT,
                "accept": "application/json",
                "origin": "https://www.bestbuy.com",
                "content-type": "application/json",
                "referer": "https://www.bestbuy.com/digitallibrary/giftcard",
                "accept-encoding": "gzip, deflate, br",
                "accept-language": "en-US,en;q=0.9",
                "cache-control": "no-cache",
            }
        )
        payload = f'{{"cardNumber":"{kwargs["card_number"]}","pin":"{kwargs["pin"]}"}}'

        logger.info("Fetching balance from API")

        resp = session.post(self.website_url, data=payload)
        if resp.status_code != 200:
            raise RuntimeError(
                f"Failed to get response from API (status code {resp.status_code})"
            )

        try:
            avail_balance = resp.json()["balance"]
        except:
            raise RuntimeError("Could not parse balance from JSON response")

        logger.info(f"Success! Card balance: {avail_balance}")
        # TODO: figure out cleaner way to do this, feature in main?
        logger.info("Sleeping 5 seconds before trying next...")
        time.sleep(5)

        return {"balance": avail_balance}

    def check_balance(self, **kwargs):
        if self.validate(kwargs):
            logger.info(f"Checking balance for card: {kwargs['card_number']}")

            return self.scrape(card_number=kwargs["card_number"], pin=kwargs["pin"])
        # else:
        # Invalid
