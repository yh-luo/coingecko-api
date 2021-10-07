# CoinGecko API wrapper (revamped)

Revamped from [pycoingecko](https://github.com/man-c/pycoingecko), a Python3 wrapper around the [CoinGecko API (V3)](https://www.coingecko.com/en/api/documentation).


## Features

- Type hinting
- `f-strings` for extra optimizations
- Flexible `Request`, e.g., use your API key for CoinGecko API plans.
- Human-friendly naming convention, e.g., `get_token_info()` instead of `get_coin_info_from_contract_address_by_id()`

## Installation

1. Clone or download this folder
2. Install the package with `pip install .` or put the `coingecko_api `folder in your project

## Usage

```python
from coingecko_api import CoinGeckoAPI
cg = CoinGeckoAPI()
```

## API documentation
[CoinGecko API documentation](https://www.coingecko.com/en/api/documentation)

### Which method is for /XXX/XXX ?

Search the API in `coingecko_api/tests/test_api.py`, remove the `test_` prefix then you have it!

#### Example

1. Search `/simple/supported_vs_currencies`
2. Found it in `test_get_supported_vs_currencies` documentation
3. `get_supported_vs_currencies` is the method for the API call.


## License

MIT