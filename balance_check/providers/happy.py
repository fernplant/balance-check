from balance_check import logger, captcha_solver, config
from balance_check.providers import blackhawk
from balance_check.providers import BalanceCheckProvider
from balance_check.validators.credit_card import Issuer, CreditCardSchema


# class Happy(BalanceCheckProvider,blackhawk.Blackhawk):
#     def __init__(self):
#         super().__init__()

#         blackhawk.Blackhawk.website_url = "https://cardholder.happycards.com/check-your-balance"
#         self.schema = CreditCardSchema([Issuer.Visa])

#     def check_balance(self, **kwargs):
#         if self.validate(kwargs):
#             logger.info(
#                 "Checking balance for card: {}, exp {}/{}".format(
#                     kwargs["card_number"], kwargs["exp_month"], kwargs["exp_year"]
#                 )
#             )

#             return blackhawk.Blackhawk.scrape(
#                 {
#                     "CardNumber": kwargs["card_number"],
#                     "ExpirationDateMonth": kwargs["exp_month"],
#                     "ExpirationDateYear": kwargs["exp_year"],
#                     "SecurityCode": kwargs["cvv"],
#                 }
#             )
