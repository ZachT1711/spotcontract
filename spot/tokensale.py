from boa.interop.Neo.Runtime import CheckWitness
from boa.interop.Neo.Action import RegisterAction
from boa.interop.Neo.Storage import Get, Put
from boa.builtins import concat
from spot.token import *
from spot.txio import get_asset_attachments
from spot.time import get_now


OnKYCRegister = RegisterAction('kyc_registration', 'address')
OnTransfer = RegisterAction('transfer', 'addr_from', 'addr_to', 'amount')
OnRefund = RegisterAction('refund', 'addr_to', 'amount')


# whitelist NEO address
def register_address(ctx, args):
    ok_count = 0
    if CheckWitness(TOKEN_OWNER):
        for address in args:
            if len(address) == 20:
                storage_key = concat(KYC_KEY, address)
                Put(ctx, storage_key, True)
                OnKYCRegister(address)
                ok_count += 1
            else:
                print("User id too short!")
    return ok_count


# Check KYC status of NEO address for token sale
def status_address(ctx, args):
    if len(args) > 0:
        addr = args[0]
        return get_status_address(ctx, addr)
    else:
        print("No address input!")
    return False


# Pull kyc status of NEO address
def get_status_address(ctx, address):
    storage_key = concat(KYC_KEY, address)
    return Get(ctx, storage_key)


# whitelist people outside NEO blockchain
def register_user_id(ctx, args):
    ok_count = 0
    if CheckWitness(TOKEN_OWNER):
        for user_id in args:
            # TODO - Need to figure out length of user_id
            if len(user_id) >= 20:
                storage_key = concat(KYC_USERID_KEY, user_id)
                Put(ctx, storage_key, True)
                OnKYCRegister(user_id)
                ok_count += 1
            else:
                print("User id too short!")
    return ok_count


# Check KYC status of user_id for token sale
def status_user_id(ctx, args):
    if len(args) > 0:
        user_id = args[0]
        return get_status_user_id(ctx, user_id)
    else:
        print("No user_id input!")
    return False


# Pull kyc status of user_id
def get_status_user_id(ctx, user_id):
    storage_key = concat(KYC_USERID_KEY, user_id)
    return Get(ctx, storage_key)


# Transfer NEO/GAS for SPOT
# Might actually disable this method in favor of just doing airdrop
# for every call because we need to handle off-chain txs anyway
def perform_exchange(ctx):

    attachments = get_asset_attachments()
    receiver_addr = attachments[0]
    sender_addr = attachments[1]
    sent_amount_neo = attachments[2]
    sent_amount_gas = attachments[3]

    exchange_ok = can_exchange(ctx, sender_addr, sent_amount_neo, sent_amount_gas, False)

    if not exchange_ok:
        # Refund neo and gas if sent
        if sent_amount_neo > 0:
            OnRefund(sender_addr, sent_amount_neo)
        if sent_amount_gas > 0:
            OnRefund(sender_addr, sent_amount_gas)
        return False

    current_balance = Get(ctx, sender_addr)

    exchanged_tokens = sent_amount_neo * TOKENS_PER_NEO / SPOT
    exchanged_tokens += sent_amount_gas * TOKENS_PER_GAS / SPOT

    new_total = exchanged_tokens + current_balance
    Put(ctx, sender_addr, new_total)

    add_to_circulation(ctx, exchanged_tokens)
    add_to_ico_token_sold(ctx, exchanged_tokens)

    OnTransfer(receiver_addr, sender_addr, exchanged_tokens)

    return True


# Test if can exchange
def can_exchange(ctx, sender_addr, sent_amount_neo, sent_amount_gas, verify_only):

    if sent_amount_gas == 0 and sent_amount_neo ==0:
        print("No neo or gas attached!")
        return False

    if not (get_status_address(ctx, sender_addr)):
        print("Address not in KYC whitelisted")
        return False

    amount_requested = sent_amount_neo * TOKENS_PER_NEO / SPOT
    amount_requested += sent_amount_gas * TOKENS_PER_GAS / SPOT

    exchange_ok = calculate_can_exchange(ctx, amount_requested, sender_addr, verify_only)

    if not exchange_ok:
        print("Failed to meet exchange conditions")

    return exchange_ok


# Check if within ICO bounds and in expected range of contribution
def calculate_can_exchange(ctx, amount, address, verify_only):

    # don't allow exchange if sale is paused
    if Get(ctx, SALE_PAUSED_KEY, True):
        print("Sale is paused")
        return False

    # Prefer to use unix timestamp
    """
    height = GetHeight()

    if height < ICO_DATE_START:
        print("Token sale has not yet begun!")
        return False

    if height > ICO_DATE_END:
        print("Token sale has ended!")
        return False
    """

    # Favor doing by unix time of latest block
    time_now = get_now()

    if time_now < ICO_DATE_START:
        print("Token sale has not yet begun!")
        return False

    if time_now > ICO_DATE_END:
        print("Token sale has ended! ")
        return False

    # Check overflow of public amount
    current_sold = Get(ctx, ICO_TOKEN_SOLD_KEY)

    new_total = current_sold + amount

    if new_total > TOKEN_TOTAL_PUBLIC:
        print("Amount would overflow amount for public sale")
        return False

    if amount < MIN_PUBLIC_AMOUNT:
        print("Must purchase at least 50 tokens")
        return False

    if amount <= MAX_PUBLIC_AMOUNT:

        # Make sure amount is less than maximum amount
        # to reserve
        current_balance = Get(ctx, address)

        if not current_balance:
            return True

        new_total = amount + current_balance

        if new_total <= MAX_PUBLIC_AMOUNT:
            return True


    print("Transaction exceeds maximum contribution")
    return False


# Reserve tokens for private placement or off-chain transcations
def reserve_tokens(ctx, args):
    """

    Airdrop Token for privatesale token buyers

    :param amount:amount of token to be airdropped
    :param to_addr:single address where token should be airdropped to
    :return:
        bool: Whether the airdrop was successful
    """
    if CheckWitness(TOKEN_OWNER):

        if len(args) == 2:

            address = args[0]

            # Reserve function needs to pass in user_id or NEO address
            # and we verify its on a whitelist for one
            whitelisted_address = get_status_address(ctx, address)
            if not whitelisted_address:
                print("Not KYC approved")
                return False

            # Second parameter is amount in Tokens
            amount = args[1] * SPOT

            # Will make sure does not exceed limit for sale
            # meets dates of sale, and does not exceed personal
            # contribution
            if not calculate_can_exchange(ctx, amount, address, False):
                print("Failed to meet exchange conditions")
                return False

            current_balance = Get(ctx, address)

            new_total = amount + current_balance

            Put(ctx, address, new_total)

            # update the in circulation amount
            add_to_circulation(ctx, amount)
            add_to_ico_token_sold(ctx, amount)

            # dispatch transfer event
            OnTransfer(TOKEN_OWNER, address, amount)

            return True

        print("Wrong args: <address> <amount>")
        return False

    print("Not contract owner")
    return False


# Check if soft cap reached
def reached_softcap(ctx):
    return get_ico_token_sold(ctx) >= ICO_SOFT_CAP


# Get tokens sold, not including team distribution
def tokens_sold(ctx):
    return get_ico_token_sold(ctx)


# Pause sale if something is going on
def pause_sale(ctx):

    if not CheckWitness(TOKEN_OWNER):
        print("Must be owner to pause sale")
        return False

    # mark the sale as paused
    Put(ctx, SALE_PAUSED_KEY, True)

    return True


# Resume sale after pause
def resume_sale(ctx):

    if not CheckWitness(TOKEN_OWNER):
        print("Must be owner to pause sale")
        return False

    # mark the sale as paused
    Put(ctx, SALE_PAUSED_KEY, False)

    return True


# mint team tokens after token sale ends, doing it after sale
# rather than before because we want to have a 2:1 ratio of
# team to public tokens, so we don't know how many team
# tokens to mint until after sale ends
def mint_team(ctx):

    if not CheckWitness(TOKEN_OWNER):
        print("You are not asset owner!")
        return False

    # If by block height
    """
    height = GetHeight()

    if height < ICO_DATE_END:
        print("Sale not yet over, need to wait to mintTeam tokens")
        return False
    """

    time_now = get_now()
    if time_now < ICO_DATE_END:
        print("Sale not yet over, need to wait to mintTeam tokens")
        return False

    if Get(ctx, TOKEN_OWNER):
        print("Already distributed team portion!")
        return False


    print("Get tokens sold")
    # Get ratio of tokens sold from 66 million (for instance 50 mil / 66 mil = 0.7575)
    sold = Get(ctx, ICO_TOKEN_SOLD_KEY)

    print("Get ratio")
    # Mint that ratio of team tokens to maintain 2:1 ratio
    # For example, if 50 mil public tokens sold, have 25 mil for team
    # Need to multiply before divide because there is no floating point support
    amount_team = (sold * TOKEN_TEAM) / TOKEN_TOTAL_PUBLIC

    print("get circ")

    current_in_circulation = Get(ctx, TOKEN_IN_CIRCULATION_KEY)

    new_total = current_in_circulation + amount_team

    if new_total > TOKEN_TOTAL_SUPPLY:
        print("Amount great than tokens available")
        return False

    # TODO
    # Put team tokens in owner address, but maybe want to change
    # this to another wallet address
    Put(ctx, TOKEN_OWNER, amount_team)

    return add_to_circulation(ctx, amount_team)
