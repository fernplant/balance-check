import re
from enum import Enum


class Merchant(Enum):
    GameStop = 'GameStop'


merchant_regex = {
    Merchant.GameStop: re.compile('^636491[0-9]{13}$')
}


def GiftCardSchema(merchants):
    def merchant_check(field, value, error):
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
                issuer_check
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
