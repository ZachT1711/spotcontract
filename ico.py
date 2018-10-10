"""
Spotcoin ICO
"""
from spot.txio import get_asset_attachments
from spot.token import *
from spot.tokensale import *
from spot.nep5 import *
from boa.interop.Neo.Runtime import GetTrigger, CheckWitness
from boa.interop.Neo.TriggerType import Application, Verification
from boa.interop.Neo.Storage import *

ctx = GetContext()
NEP5_METHODS = ['name', 'symbol', 'decimals', 'totalSupply', 'balanceOf', 'transfer', 'transferFrom', 'approve', 'allowance']


def Main(operation, args):

    trigger = GetTrigger()

    if trigger == Verification():
        is_owner = CheckWitness(TOKEN_OWNER)
        if is_owner:
            return True

        # No mintToken like regular NEO crowdsale.
        # Spotcoin takes offchain transactions (BTC, ETH, etc.)
        # So all tokens are created through `airdrop` method
        # after payment has been processed
        return False

    elif trigger == Application():

        for op in NEP5_METHODS:
            if operation == op:
                return handle_nep51(ctx, operation, args)

        if operation == 'deploy':
            return deploy()

        if operation == 'circulation':
            return get_circulation(ctx)

        if operation == 'mintTokens':
            return perform_exchange(ctx)

        if operation == 'tokensale_register':
            return register_address(ctx, args)

        if operation == 'tokensale_status':
            return status_address(ctx, args)

        if operation == 'tokensale_available':
            return public_sale_available(ctx)

        if operation == 'get_attachments':
            return get_asset_attachments()

        if operation == 'airdrop':
            return reserve_tokens(ctx, args)

        if operation == 'tokens_sold':
            return tokens_sold(ctx)

        if operation == 'mint_team':
            return mint_team(ctx)

        if operation == 'pause_sale':
            return pause_sale(ctx)

        if operation == 'resume_sale':
            return resume_sale(ctx)

        if operation == 'end_sale':
            return end_sale(ctx)

        return 'unknown operation'

    return False


def deploy():

    if not CheckWitness(TOKEN_OWNER):
        print("You are not asset owner!")
        return False

    # Can only deploy once
    if not Get(ctx, 'initialized'):
        Put(ctx, 'initialized', 1)
        # Set to zero
        Put(ctx, TOKEN_IN_CIRCULATION_KEY, 0)
        Put(ctx, ICO_TOKEN_SOLD_KEY, 0)
        return True

    print("Contract already deployed!")
    return False
