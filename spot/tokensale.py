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


# Add address as private placement, has implications on withdrawl
# and allow minting more than 1 million tokens
def add_private_placement(ctx, address):
    print("Adding private placement address")
    if CheckWitness(TOKEN_OWNER):
        if len(address) == 20:
            storage_key = concat(PP_KEY, address)
            Put(ctx, storage_key, True)
            return True
    return False


# Check if address already in private placement list
def is_private_placement(ctx, address):
    storage_key = concat(PP_KEY, address)
    if Get(ctx, storage_key):
        return True
    return False


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
                print("Address too short!")
    return ok_count


# Check KYC status of NEO address for token sale
def status_address(ctx, args):
    if len(args) > 0:
        addr = args[0]
        if len(addr) != 20:
            print("Invalid address length")
            return False
        return get_status_address(ctx, addr)
    else:
        print("No address input!")
    return False


# Pull kyc status of NEO address
def get_status_address(ctx, address):
    storage_key = concat(KYC_KEY, address)
    return Get(ctx, storage_key)


# MintTokens is disabled for the sale. Spotcoin will mint all tokens with
# reserve_tokens function after user has passed KYC on the website. Spotcoin
# will generate a deposit address for the sale which will be visible on the
# blockchain. Users may withdrawl from this address after Spotcoin has performed
# and released a third party audit detailing the entire sale
def perform_exchange(ctx):

    attachments = get_asset_attachments()
    receiver_addr = attachments[0]
    sender_addr = attachments[1]
    sent_amount_neo = attachments[2]
    sent_amount_gas = attachments[3]

    print("mintTokens disabled for sale! Must use Spotcoin website!")

    # Refund neo and gas if sent
    if sent_amount_neo > 0:
        OnRefund(sender_addr, sent_amount_neo)
    if sent_amount_gas > 0:
        OnRefund(sender_addr, sent_amount_gas)
    return False


# Check if within ICO bounds and in expected range of contribution
def calculate_can_exchange(ctx, amount, address, verify_only, is_private):


    # don't allow exchange if sale is paused
    if Get(ctx, SALE_PAUSED_KEY):
        print("Sale is paused")
        return False

    # don't allow exchange if sale has been ended
    if Get(ctx, END_SALE_KEY):
        print("Sale has ended!")
        return False

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


    # Only need to check maximum contribution for non-private placement
    if is_private:
        return True

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


# Reserve tokens for people who have contributed to the
# tokensale via private placement, btc, eth, sib, neo, gas
# or usd/euro
def reserve_tokens(ctx, args):
    """
    :param amount:amount of token to be airdropped
    :param to_addr:single address where token should be airdropped to
    :param is_priv_placement:boolean to determine if the reservation is for private placement
    :return:
        bool: Whether the airdrop was successful
    """
    if CheckWitness(TOKEN_OWNER):

        if len(args) == 3:

            if len(args[0]) != 20:
                print("Invalid address")
                return False

            address = args[0]

            # Reserve function needs to pass in NEO address
            # and we verify its on a whitelist for one
            if not get_status_address(ctx, address):
                print("Not KYC approved")
                return False

            # Second parameter is amount in Tokens
            amount = args[1] * SPOT

            if amount < 1:
                print("Insufficient amount")
                return False

            # Third parameter is if this is private placement
            # and dictates if tokens have a lockup period
            is_private = False
            if args[2] is True:
                is_private = True


            if is_private and not is_private_placement(ctx, address):
                success = add_private_placement(ctx, address)


            # Will make sure does not exceed limit for sale
            # meets dates of sale, and does not exceed personal
            # contribution
            exchange_ok = calculate_can_exchange(ctx, amount, address, False, is_private)
            if not exchange_ok:
                print("Failed to meet exchange conditions")
                return False

            current_balance = Get(ctx, address)

            new_total = amount + current_balance

            Put(ctx, address, new_total)

            # update the in circulation amount
            success = add_to_circulation(ctx, amount)
            success = add_to_ico_token_sold(ctx, amount)

            # dispatch transfer event
            OnTransfer(TOKEN_OWNER, address, amount)

            return True

        print("Wrong args: <address> <amount> <is_private_placement>")
        return False

    print("Not contract owner")
    return False


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

# End sale completely. Totally non-reversible action
# but allows sale to end early
def end_sale(ctx):

    if not CheckWitness(TOKEN_OWNER):
        print("Must be owner to end sale")
        return False

    # mark the sale as paused
    Put(ctx, END_SALE_KEY, True)

    return True

# mint team tokens after token sale ends, doing it after sale
# rather than before because we want to have a 2:1 ratio of
# team to public tokens, so we don't know how many team
# tokens to mint until after sale ends
def mint_team(ctx):

    if not CheckWitness(TOKEN_OWNER):
        print("You are not asset owner!")
        return False

    # Can allow mint_team if after ICO_DATE_END or if END_SALE_KEY
    # has been set.
    ended_by_owner = Get(ctx, END_SALE_KEY)

    time_now = get_now()
    if time_now < ICO_DATE_END and not ended_by_owner:
        print("Sale not yet over, need to wait to mintTeam tokens")
        return False

    if Get(ctx, TEAM_ADDRESS):
        print("Already distributed team portion!")
        return False


    # Get ratio of tokens sold from 66 million (for instance 50 mil / 66 mil = 0.7575)
    sold = Get(ctx, ICO_TOKEN_SOLD_KEY)

    # Mint that ratio of team tokens to maintain 2:1 ratio
    # For example, if 50 mil public tokens sold, have 25 mil for team
    # Need to multiply before divide because there is no floating point support
    amount_team = (sold * TOKEN_TEAM) / TOKEN_TOTAL_PUBLIC

    current_in_circulation = Get(ctx, TOKEN_IN_CIRCULATION_KEY)

    new_total = current_in_circulation + amount_team

    if new_total > TOKEN_TOTAL_SUPPLY:
        print("Amount greater than tokens available")
        return False

    # TODO
    # Put team tokens in owner address, but maybe want to change
    # this to another wallet address
    Put(ctx, TEAM_ADDRESS, amount_team)

    return add_to_circulation(ctx, amount_team)
