"""
SPOTCOIN ICO Contract
"""

from boa.interop.Neo.Storage import *

TOKEN_NAME = 'Spotcoin'
TOKEN_SYMBOL = 'SPOT'
TOKEN_DECIMALS = 8

# Owner address
TOKEN_OWNER = b'\xb7\xfc\xfa\xe3\xb7O\xaf\xd4\xd3\xfeR\xec+\xd3A\x92\xd7\xbf\x12\r'

# If wanting to store team tokens in a different wallet
TEAM_ADDRESS = b'\xb7\xfc\xfa\xe3\xb7O\xaf\xd4\xd3\xfeR\xec+\xd3A\x92\xd7\xbf\x12\r'

# Shorthand for 1 SPOT is 8 decimal places
SPOT = 100000000

# 99 million
TOKEN_TOTAL_SUPPLY = 99000000 * 100000000

# 66 million sold to public
TOKEN_TOTAL_PUBLIC = 66000000 * 100000000

# Max 33 million for team. Really only mints enough
# to match a 2:1 ratio of public sale tokens
TOKEN_TEAM = 33000000 * 100000000

# MAX anyone from public can purchase is 1 million SPOT
# Private placement amounts are tagged by address and timelocked
MAX_PUBLIC_AMOUNT = 1000000 * 100000000

# Must buy more than 50 SPOT in public sale
# but different promotions allows someone to
# get smaller amounts, so disable less than one
MIN_PUBLIC_AMOUNT = 1 * 100000000

# For mainnet

# October 18th 2018 @ 00:00 GMT
ICO_DATE_START = 1539820800

# November 9th 2018 @ 0000 UTC
ICO_DATE_END = 1541167200

# Storage keys
TOKEN_IN_CIRCULATION_KEY = b'in_circulation'
KYC_KEY = b'kyc_neo_address'
ICO_TOKEN_SOLD_KEY = b'tokens_sold_in_ico'
SALE_PAUSED_KEY = b'sale_paused'
END_SALE_KEY = b'sale_over'
PP_KEY = b'priv_placement'


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
