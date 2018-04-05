"""
SPOTCOIN ICO Contract
"""

from boa.interop.Neo.Storage import *

TOKEN_NAME = 'Spotcoin'
TOKEN_SYMBOL = 'SPOT'
TOKEN_DECIMALS = 8

# TODO - enter this when we know the NEO address we want to deposit to
# Uses this temporarily for private net
TOKEN_OWNER = b'#\xba\'\x03\xc52c\xe8\xd6\xe5"\xdc2 39\xdc\xd8\xee\xe9'

# Shorthand for 1 SPOT is 8 decimal places
SPOT = 100000000

# 99 million
TOKEN_TOTAL_SUPPLY = 99000000 * 100000000

# 66 million sold to public
TOKEN_TOTAL_PUBLIC = 66000000 * 100000000

# Reserved 33 million for team at start of token
# contract
TOKEN_TEAM = 33000000 * 100000000

# About 0.50 USD per token as of April 3
TOKENS_PER_NEO = 102 * 100000000
TOKENS_PER_GAS = 32 * 100000000

# MAX public an buy is 1 million tokens
MAX_PUBLIC_AMOUNT = 1000000 * 100000000

# Must buy more than 50 SPOT
MIN_PUBLIC_AMOUNT = 50 * 100000000

# Soft cap at 6 million
ICO_SOFT_CAP = 6000000 * 100000000

# May 1st 2018 @ 1400 UTC (1800 Tbilisi)
ICO_DATE_START = 1525183200

# June 1st 2018 @ 1400 UTC (1800 Tbilisi)
ICO_DATE_END = 1527861600

"""
# When testing in private Net, set this to true
ICO_DATE_START = 1522823407 + 60*5
ICO_DATE_END = 1522827663 + 60*34
"""


# Storage keys
TOKEN_IN_CIRCULATION_KEY = b'in_circulation'
KYC_KEY = b'kyc_neo_address'
KYC_USERID_KEY = b'kyc_userid'
ICO_TOKEN_SOLD_KEY = b'tokens_sold_in_ico'
LIMITED_ROUND_KEY = b'r1'
SALE_PAUSED_KEY = b'sale_paused'


def amount_available(ctx):
    """

     :return: int The total amount of tokens available
    """
    in_circulation = Get(ctx, TOKEN_IN_CIRCULATION_KEY)
    available = TOKEN_TOTAL_SUPPLY - in_circulation
    return available


def add_to_circulation(ctx, amount):
    """
    Adds an amount of token to circulation

    :param amount: int the amount to add to circulation
    """
    current_supply = Get(ctx, TOKEN_IN_CIRCULATION_KEY)
    current_supply += amount
    Put(ctx, TOKEN_IN_CIRCULATION_KEY, current_supply)
    return True


def get_circulation(ctx):
    """
    Get the total amount of tokens in circulation
    The extra addition is a workaround to get the correct numerical value printed,
    otherwise it prints in little endian

     :return: int The total amount of tokens in circulation
    """
    in_circ = Get(ctx, TOKEN_IN_CIRCULATION_KEY)

    available = TOKEN_TOTAL_SUPPLY - in_circ

    in_circ = TOKEN_TOTAL_SUPPLY - available

    return in_circ


def public_sale_available(ctx):
    """

     :return: int The amount of tokens left for sale in the crowdsale
    """
    current_sold = Get(ctx, ICO_TOKEN_SOLD_KEY)
    available = TOKEN_TOTAL_PUBLIC - current_sold
    return available


def add_to_ico_token_sold(ctx, amount):
    """
    Adds an amount of token to ico_token_sold

    :param amount: int the amount to add to ico_token_sold
    """
    current_sold = Get(ctx, ICO_TOKEN_SOLD_KEY)
    current_sold += amount
    Put(ctx, ICO_TOKEN_SOLD_KEY, current_sold)
    return True


def get_ico_token_sold(ctx):
    """
    Get the total amount of tokens in ico_token_sold
    The extra addition is a workaround to get the correct numerical value printed, otherwise
    it prints in little endian

    :return:
        int: Total amount in ico_token_sold
    """
    sold = Get(ctx, ICO_TOKEN_SOLD_KEY)

    available = TOKEN_TOTAL_PUBLIC - sold

    sold = TOKEN_TOTAL_PUBLIC - available

    return sold
