## Test contract in privatenet
Need to install privatenet docker image with instructions [here](https://medium.com/proof-of-working/how-to-run-a-private-network-of-the-neo-blockchain-d83004557359)

#### Start privatenet and import wallet / claim gas
```
# Start in privatenet
np-prompt -p

# Open wallet
neo> open wallet fixtures/neo-privnet.wallet
[Password]> coz
Opened wallet at neo-privnet.wallet
neo> wallet rebuild
```

Wait a few moments and claim gas so you can deploy the contract. First you must send 1 NEO to yourself to be able to claim the gas
```
neo> send neo AK2nJJpJr6o664CWJKi1QRXjqeic2zRp8y 1
```
Wait for tx to confirm in next block... and gas should now be claimable with:
```
neo> wallet claim
```

#### Import Contract

Now import contract and deploy
```
neo> import contract ico.avm 0710 05 True False False
[password]> coz
[name]> Spotcoin ICO
# ... enter contract info ...
```

You can verify the contract and find the contract hash with:
```
neo> contract search Spot
```
Should be something like: `0x2830fc346b1c7a350914fbaea5ef7b3fbe3c994c`, this will be used to with `testinvoke` for all contract methods from this point forward

You can also verify a transaction has finished with
```
neo> tx <txhash>
```

#### Deploy Contract
```
neo> testinvoke 0x2830fc346b1c7a350914fbaea5ef7b3fbe3c994c deploy []
```
Test cannot deploy twice
```
neo> testinvoke 0x2830fc346b1c7a350914fbaea5ef7b3fbe3c994c deploy []
```

#### TURN ON CONTRACT LOGGING
This will let you view `print()` statements that execute inside the contract
```
neo> config sc-events on
```

#### Check amount left for sale / in circulation

Amount left in sale: 66 million at beginning of sale
```
neo> testinvoke 0x2830fc346b1c7a350914fbaea5ef7b3fbe3c994c tokensale_available []
```

Total in circulation thus far: 0 at beginning of sale
```
neo> testinvoke 0x2830fc346b1c7a350914fbaea5ef7b3fbe3c994c circulation []
```

Total tokens sold thus far: 0 at beginning of sale
```
neo> testinvoke 0x2830fc346b1c7a350914fbaea5ef7b3fbe3c994c tokens_sold []
```


#### Register User and Verify KYC status
```
neo> testinvoke 0x2830fc346b1c7a350914fbaea5ef7b3fbe3c994c tokensale_register ["AHbZkoUi6mjEMwcs13cWwayVUHxJEj6Dtx"]
# wait for transaction to sync...
neo> testinvoke 0x2830fc346b1c7a350914fbaea5ef7b3fbe3c994c tokensale_status ["AHbZkoUi6mjEMwcs13cWwayVUHxJEj6Dtx"]

# Try an unverified user
neo> testinvoke 0x2830fc346b1c7a350914fbaea5ef7b3fbe3c994c tokensale_status ["AK2nJJpJr6o664CWJKi1QRXjqeic2zRp8y"]
```

Can also import many addresses at once
```
testinvoke 0x2830fc346b1c7a350914fbaea5ef7b3fbe3c994c tokensale_register ["AHbZkoUi6mjEMwcs13cWwayVUHxJEj6Dtx", "ASRuk8ggWiFaC7LNmYGkC8kTeELNSi6Wz9", "ASTibgUJSJe7PoRZdkGM8hSmpiHFgoDgZP", "AQygubFSHbFJP7gWsqZEy8LJR1PijAmtv7", "AGDtLGawthnez5CHKjNzAMhfxhK99YKXYf", "AQbFDgZuNxi4LyUVzrydcvSuQuAx1vQ9rP", "AMRcVTgFWDYBQSEHt8sa3RVJkapYFq4dyB", "ARzuN5Rc8Mdv6bLDswETBzwbBuMJXQVWYW"]
```

#### Pause and Resume Contract
```
neo> testinvoke 0x2830fc346b1c7a350914fbaea5ef7b3fbe3c994c pause_sale []
```
And resume
```
neo> testinvoke 0x2830fc346b1c7a350914fbaea5ef7b3fbe3c994c resume_sale []
```

#### End Sale 
We call this method if Spotcoin closes the sale before the ICO_END_DATE
which was set to a point further in the future than expected
```
neo> testinvoke 0x2830fc346b1c7a350914fbaea5ef7b3fbe3c994c end_sale []
```

#### Airdrop tokens for KYC'd user

Airdrop 10,000 tokens for a KYC'd user
```
neo> testinvoke 0x2830fc346b1c7a350914fbaea5ef7b3fbe3c994c airdrop ["AHbZkoUi6mjEMwcs13cWwayVUHxJEj6Dtx", 10000, False]
```
Verify the balance is correct

```
neo> testinvoke 0x2830fc346b1c7a350914fbaea5ef7b3fbe3c994c balanceOf ["AHbZkoUi6mjEMwcs13cWwayVUHxJEj6Dtx"]
```

Airdrop of less than 50 tokens is invalid
```
neo> testinvoke 0x2830fc346b1c7a350914fbaea5ef7b3fbe3c994c airdrop ["AHbZkoUi6mjEMwcs13cWwayVUHxJEj6Dtx", 49, False]
```

Airdrop of over 1,000,000 tokens is invalid
```
neo> testinvoke 0x2830fc346b1c7a350914fbaea5ef7b3fbe3c994c airdrop ["AHbZkoUi6mjEMwcs13cWwayVUHxJEj6Dtx", 1000001, False]
```

Limited to 1,000,000 total through several buys
```
# Reserve of 900,000 should pass
neo> testinvoke 0x2830fc346b1c7a350914fbaea5ef7b3fbe3c994c airdrop ["AHbZkoUi6mjEMwcs13cWwayVUHxJEj6Dtx", 900000, False]
# Reserve of 100,001 should fail because now over 1,000,000 total
neo> testinvoke 0x2830fc346b1c7a350914fbaea5ef7b3fbe3c994c airdrop ["AHbZkoUi6mjEMwcs13cWwayVUHxJEj6Dtx", 100001, False]
```

Airdrop private placement, which can exceed limit of 1,000,000 SPOT
```
neo> testinvoke 0x2830fc346b1c7a350914fbaea5ef7b3fbe3c994c airdrop ["AQbFDgZuNxi4LyUVzrydcvSuQuAx1vQ9rP", 2000001, True]
```

#### Purchase tokens via NEO/GAS

This function is disabled for the Spotcoin ICO, and will issue a refund to the user. The reason
is that tokens will not be immediately distributed, but held in escrow address until the public
audit of the ICO is complete.
```
neo> testinvoke 0x2830fc346b1c7a350914fbaea5ef7b3fbe3c994c mintTokens [] --attach-neo=5 --attach-gas=5

```

#### Mint team tokens

Must be after ICO_DATE_END
```
neo> testinvoke 0x2830fc346b1c7a350914fbaea5ef7b3fbe3c994c mint_team []
```
Will deposit tokens in `TEAM_ADDRESS`

#### NEP-5
neo> testinvoke 0x2830fc346b1c7a350914fbaea5ef7b3fbe3c994c name []
neo> testinvoke 0x2830fc346b1c7a350914fbaea5ef7b3fbe3c994c decimals []
neo> testinvoke 0x2830fc346b1c7a350914fbaea5ef7b3fbe3c994c symbol []
neo> testinvoke 0x2830fc346b1c7a350914fbaea5ef7b3fbe3c994c totalSupply []
neo> testinvoke 0x2830fc346b1c7a350914fbaea5ef7b3fbe3c994c balanceOf ["AHbZkoUi6mjEMwcs13cWwayVUHxJEj6Dtx"]
neo> testinvoke 0x2830fc346b1c7a350914fbaea5ef7b3fbe3c994c transfer ["AK2nJJpJr6o664CWJKi1QRXjqeic2zRp8y", "AQbFDgZuNxi4LyUVzrydcvSuQuAx1vQ9rP", 100]
neo> testinvoke 0x2830fc346b1c7a350914fbaea5ef7b3fbe3c994c approve ["AK2nJJpJr6o664CWJKi1QRXjqeic2zRp8y", "AQbFDgZuNxi4LyUVzrydcvSuQuAx1vQ9rP", 100]
neo> testinvoke 0x2830fc346b1c7a350914fbaea5ef7b3fbe3c994c allowance ["AK2nJJpJr6o664CWJKi1QRXjqeic2zRp8y", "AQbFDgZuNxi4LyUVzrydcvSuQuAx1vQ9rP"]
neo> testinvoke 0x2830fc346b1c7a350914fbaea5ef7b3fbe3c994c transferFrom ["AK2nJJpJr6o664CWJKi1QRXjqeic2zRp8y", "AQbFDgZuNxi4LyUVzrydcvSuQuAx1vQ9rP", 100]


#### Import token and check balance
You can import token and view the balance in any wallet SPOT was sent to
```
neo> import token 0x2830fc346b1c7a350914fbaea5ef7b3fbe3c994c
neo> wallet
```

### Send SPOT from one wallet to another
```
neo> wallet  # Look at asset-id of SPOT token
neo> send <asset-id> AZDUDZwMntbW9VBwBciMfmi97Gxf4PoHBB 100 --from-addr=AW5FzuRdoZcszcE4krvtFEnGSCsECAkJan
```

#### Test non-owner cannot call owner methods
Open non-owner wallet (create one with `create wallet` if it doesn't exist), may also need to send this wallet GAS from the privnet wallet before you can use `testinvoke`
```
neo> open wallet fixtures/non-owner.wallet
[password]> testpassword
neo> testinvoke 0x2830fc346b1c7a350914fbaea5ef7b3fbe3c994c airdrop ["AHbZkoUi6mjEMwcs13cWwayVUHxJEj6Dtx", 1000]
```
