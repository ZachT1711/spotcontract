# Spotcoin ICO Contract v2

The contract is deployed on Neo MainNet with Script Hash `0x2830fc346b1c7a350914fbaea5ef7b3fbe3c994c`

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

### How this works

After the contract is deployed, the Spotcoin forces users to go through a KYC process on [spotcoin.com](www.spotcoin.com), and they will be generated a deposit address that Spotcoin manages after passing KYC. This address will be whitelisted in our contract via the `tokensale_register` method.

Upon contribution on our site via USD, BTC, ETH, GAS, etc., we call the `airdrop` function to reserve X amount of SPOT tokens for that address given the current market rates, which are calculated on our backend.

The contract will ensure that this happens within the ICO period and the user is limited to getting a maximum of 1 million SPOT for public contributions.

After the ICO period has ended, we (the contract owner) will call `mint_team` - which will create team tokens, in order to maintain the 2-1 ratio of public-to-team tokens.
