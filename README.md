# Spotcoin ICO Contract

Deployed on Neo MainNet with Script Hash `0x4ce5de1c7de5db3f69850578ea975af8c503fff7`

## Details 

### Requirements

Usage requires Python 3.6+

### Installation

Clone the repository and navigate into the project directory. 
Make a Python 3 virtual environment and activate it via

```shell
python3 -m venv venv
source venv/bin/activate
```

or to explicitly install Python 3.6 via

```shell
virtualenv -p /usr/local/bin/python3.6 venv
source venv/bin/activate
```

Then install the requirements via

```shell
pip install -r requirements.txt
```

### Compilation

The template may be compiled as follows

```python
python3 compile.py
```

### Running contract
See [Test README](tests/README.md)

### How this is going to work

After the contract is deployed, the Spotcoin forces users to go through a KYC process through our site, and they will only be generated a deposit address that spotcoin manages after passing KYC. This address will be whitelisted in our contract via the `tokensale_register` method.

Upon contribution on our site via USD, BTC, ETH, GAS, etc., we will call the `airdrop` function to reserve X amount of SPOT tokens for that address given the current market rates, which are calculated on our backend.

The contract will ensure that this happens within the ICO period and the user is limited to getting a maximum of 1 million SPOT. 

The `reached_softcap` function can be called to see if the soft-cap of 6 million tokens has been reached. 

After the ICO period has ended, we (the contract owner) will call `mint_team` - which will create team tokens, in order to maintain the 2-1 ratio of public-to-team tokens.
