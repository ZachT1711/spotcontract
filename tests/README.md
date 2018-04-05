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
neo> import contract ico.avm 0710 05 True False
[password]> coz
[name]> Spotcoin ICO
# ... enter contract info ...
```

You can verify the contract and find the contract hash with:
```
neo> contract search Spot
```
Should be something like: `0x225efc872abd47572f361d3b92a30015e8db83b6`, this will be used to with `testinvoke` for all contract methods from this point forward

You can also verify a transaction has finished with
```
neo> tx <txhash>
```

#### Deploy Contract
```
neo> testinvoke 0x225efc872abd47572f361d3b92a30015e8db83b6 deploy []
```
Test cannot deploy twice
```
neo> testinvoke 0x225efc872abd47572f361d3b92a30015e8db83b6 deploy []
```

#### TURN ON CONTRACT LOGGING
This will let you view `print()` statements that execute inside the contract
```
neo> config sc-events on
```

#### Check amount left for sale / in circulation

Amount left in sale: 66 million at beginning of sale
```
neo> testinvoke 0x225efc872abd47572f361d3b92a30015e8db83b6 tokensale_available []
```

Total in circulation thus far: 0 at beginning of sale
```
neo> testinvoke 0x225efc872abd47572f361d3b92a30015e8db83b6 circulation []
```

Total tokens sold thus far: 0 at beginning of sale
```
neo> testinvoke 0x225efc872abd47572f361d3b92a30015e8db83b6 tokens_sold []
```


#### Register User and Verify KYC status
```
neo> testinvoke 0x225efc872abd47572f361d3b92a30015e8db83b6 tokensale_register ["AHbZkoUi6mjEMwcs13cWwayVUHxJEj6Dtx"]
# wait for transaction to sync...
neo> testinvoke 0x225efc872abd47572f361d3b92a30015e8db83b6 tokensale_status ["AHbZkoUi6mjEMwcs13cWwayVUHxJEj6Dtx"]  

# Try an unverified user
neo> testinvoke 0x225efc872abd47572f361d3b92a30015e8db83b6 tokensale_status ["AK2nJJpJr6o664CWJKi1QRXjqeic2zRp8y"]  
```
1 2 3 4 5

Can also import many addresses at once
```
testinvoke 0x225efc872abd47572f361d3b92a30015e8db83b6 tokensale_register ["AJMUb1uc8Z6pgoMnR3T4Cme94qs38p3tfU", "ASRuk8ggWiFaC7LNmYGkC8kTeELNSi6Wz9", "ASTibgUJSJe7PoRZdkGM8hSmpiHFgoDgZP", "AQygubFSHbFJP7gWsqZEy8LJR1PijAmtv7", "AGDtLGawthnez5CHKjNzAMhfxhK99YKXYf", "AQbFDgZuNxi4LyUVzrydcvSuQuAx1vQ9rP", "AMRcVTgFWDYBQSEHt8sa3RVJkapYFq4dyB", "ARzuN5Rc8Mdv6bLDswETBzwbBuMJXQVWYW"]
```

#### Pause and Resume Contract
```
neo> testinvoke 0x225efc872abd47572f361d3b92a30015e8db83b6 pause_sale []
```
And resume
```
neo> testinvoke 0x225efc872abd47572f361d3b92a30015e8db83b6 resume_sale []
```

#### Airdrop tokens for KYC'd user

Airdrop 10,000 tokens for a KYC'd user
```
neo> testinvoke 0x225efc872abd47572f361d3b92a30015e8db83b6 airdrop ["AHbZkoUi6mjEMwcs13cWwayVUHxJEj6Dtx", 10000] 
```
Verify the balance is correct

```
neo> testinvoke 0x225efc872abd47572f361d3b92a30015e8db83b6 balanceOf ["AHbZkoUi6mjEMwcs13cWwayVUHxJEj6Dtx"]
```

Airdrop of less than 50 tokens is invalid
```
neo> testinvoke 0x225efc872abd47572f361d3b92a30015e8db83b6 airdrop ["AHbZkoUi6mjEMwcs13cWwayVUHxJEj6Dtx", 49] 
```

Airdrop of over 1,000,000 tokens is invalid
```
neo> testinvoke 0x225efc872abd47572f361d3b92a30015e8db83b6 airdrop ["AHbZkoUi6mjEMwcs13cWwayVUHxJEj6Dtx", 1000001] 
```

Limited to 1,000,000 total through several buys
```
# Reserve of 900,000 should pass
neo> testinvoke 0x225efc872abd47572f361d3b92a30015e8db83b6 airdrop ["AHbZkoUi6mjEMwcs13cWwayVUHxJEj6Dtx", 900000] 
# Reserve of 100,001 should fail because now over 1,000,000 total
neo> testinvoke 0x225efc872abd47572f361d3b92a30015e8db83b6 airdrop ["AHbZkoUi6mjEMwcs13cWwayVUHxJEj6Dtx", 100001] 
```

#### Purchase tokens via NEO/GAS

This will send gas from the current wallet, so you need to make sure the wallet address is white listed
and there exist GAS and NEO
```
neo> testinvoke 0x225efc872abd47572f361d3b92a30015e8db83b6 mintTokens [] --attach-neo=5 --attach-gas=5

```

#### Import token 
You can import token and view the balance in your wallet with
```
neo> import token 0x225efc872abd47572f361d3b92a30015e8db83b6
neo> wallet
```

#### Mint team tokens

Must be after ICO_DATE_END
```
neo> testinvoke 0x225efc872abd47572f361d3b92a30015e8db83b6 mint_team []
```

#### Test non-owner cannot call owner methods
Open non-owner wallet (create one with `create wallet` if it doesn't exist), may also need to send this wallet GAS from the privnet wallet before you can use `testinvoke`
```
neo> open wallet non-owner.wallet
[password]> testpassword
neo> testinvoke 0x225efc872abd47572f361d3b92a30015e8db83b6 airdrop ["AHbZkoUi6mjEMwcs13cWwayVUHxJEj6Dtx", 1000]
```
