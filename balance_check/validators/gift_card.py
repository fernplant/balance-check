import re
from enum import Enum
from luhn import verify


class Merchant(Enum):
    GameStop = 'GameStop'


merchant_regex = {
    Merchant.GameStop: re.compile('636491[0-9]{13}')
}


def luhn_check(field, value, error):
    if not verify(value):
        error(field, "does not pass Luhn check")


def GiftCardSchema(merchants):
    def issuer_check(field, value, error):
        if not any(merchant_regex[merchant].match(value) for merchant in merchants):
            error(field, "invalid card number for merchant(s): {}".format(
                ", ".join([merchant.value for merchant in merchants])
            ))

    return {
        "card_number": {
            "required": True,
            "type": "string",
            "empty": False,
            "validator": [
                issuer_check,
                luhn_check
            ]
        },
        "pin": {
            "required": True,
            "type": "string",
            "minlength": 4,
            "maxlength": 8,
            "empty": False
        }
    }
