from typing import Any, Dict, List, Optional, Union

from requests import Request, Response, Session

__version__ = '0.1.0'


class CoinGeckoAPI:
    _ENDPOINT = 'https://api.coingecko.com/api/v3/'
    _CONNECT_TIMEOUT_S = 5

    def __init__(self) -> None:
        self.session = Session()

    def _request(self, method: str, path: str, **kwargs) -> Any:
        request = Request(method, self._ENDPOINT + path, **kwargs)
        response = self.session.send(request.prepare(),
                                     timeout=self._CONNECT_TIMEOUT_S)
        return self._process_response(response)

    def _process_response(self, response: Response) -> Any:
        try:
            data = response.json()
        except ValueError:
            response.raise_for_status()
            raise
        return data

    def _process_params(self,
                        api_path: str,
                        params: Optional[Dict[str, Any]] = None,
                        api_has_params: bool = False) -> str:
        if params:
            api_path += '&' if api_has_params else '?'
            for key, val in params.items():
                if type(val) == bool:
                    val = str(val).lower()
                api_path += f'{key}={val}&'
            api_path = api_path[:-1]  # remove the redundant '&'
        return api_path

    # ping
    def ping(self) -> dict:
        """Check API server status."""
        return self._request('GET', 'ping')

    # simple
    def get_simple_price(self,
                         ids: Union[str, List[str]],
                         vs_currencies: Union[str, List[str]],
                         params: Optional[Dict[str, Any]] = None) -> dict:
        """Get the current price of cryptocurrencies."""
        ids_str = ','.join(ids) if type(ids) == list else ids
        vs_str = ','.join(vs_currencies) if type(
            vs_currencies) == list else vs_currencies
        _params = {'ids': ids_str, 'vs_currencies': vs_str}
        if params:
            _params.update(params)
        api_path = self._process_params('simple/price', _params)
        return self._request('GET', api_path)

    def get_simple_token_price(
            self,
            id: str,
            contract_addresses: Union[str, List[str]],
            vs_currencies: Union[str, List[str]],
            params: Optional[Dict[str, Any]] = None) -> dict:
        """Get current price of tokens for a given platform (id)."""
        addrs_str = ','.join(contract_addresses) if type(
            contract_addresses) == list else contract_addresses
        vs_str = ','.join(vs_currencies) if type(
            vs_currencies) == list else vs_currencies
        _params = {'contract_addresses': addrs_str, 'vs_currencies': vs_str}
        if params:
            _params.update(params)
        api_path = self._process_params(f'simple/token_price/{id}', _params)
        return self._request('GET', api_path)

    def get_supported_vs_currencies(self) -> List[str]:
        """Get list of supported vs_currencies."""
        return self._request('GET', 'simple/supported_vs_currencies')

    # coins
    def list_coins(self) -> List[dict]:
        """List all supported coins (no pagination required)."""
        return self._request('GET', 'coins/list')

    def list_coins_markets(
            self,
            vs_currency: str,
            params: Optional[Dict[str, Any]] = None) -> List[dict]:
        """List all supported coins price and market related data."""
        _params = {'vs_currency': vs_currency}
        if params:
            _params.update(params)
        api_path = self._process_params(f'coins/markets', _params)
        return self._request('GET', api_path)

    def get_coin(self,
                 id: str,
                 params: Optional[Dict[str, Any]] = None) -> dict:
        """Get current data for a coin."""
        api_path = self._process_params(f'coins/{id}', params)
        return self._request('GET', api_path)

    def get_coin_tickers(self,
                         id: str,
                         params: Optional[Dict[str, Any]] = None) -> dict:
        """Get coin tickers (paginated to 100 items)."""
        api_path = self._process_params(f'coins/{id}/tickers', params)
        return self._request('GET', api_path)

    def get_coin_history(self,
                         id: str,
                         date: str,
                         params: Optional[Dict[str, Any]] = None) -> dict:
        """Get historical data at a given date for a coin."""
        _params = {'date': date}
        if params:
            _params.update(params)
        api_path = self._process_params(f'coins/{id}/history', _params)
        return self._request('GET', api_path)

    def get_coin_market_chart(self,
                              id: str,
                              vs_currency: str,
                              days: Union[int, str],
                              params: Optional[Dict[str, Any]] = None) -> dict:
        """Get historical market data for a coin."""
        _params = {'vs_currency': vs_currency, 'days': days}
        if params:
            _params.update(params)
        api_path = self._process_params(f'coins/{id}/market_chart', _params)
        return self._request('GET', api_path)

    def get_coin_market_chart_range(
            self,
            id: str,
            vs_currency: str,
            from_unix_ts: int,
            to_unix_ts: int,
            params: Optional[Dict[str, Any]] = None) -> dict:
        """Get historical market data within a range of time for a coin."""
        if from_unix_ts > to_unix_ts:
            raise ValueError('from_unix_tx should be smaller than to_unix_ts.')

        _params = {
            'vs_currency': vs_currency,
            'from': from_unix_ts,
            'to': to_unix_ts
        }
        if params:
            _params.update(params)
        api_path = self._process_params(f'coins/{id}/market_chart/range',
                                        _params)
        return self._request('GET', api_path)

    def get_coin_status(self,
                        id: str,
                        params: Optional[Dict[str, Any]] = None) -> dict:
        """Get status updates for a given coin."""
        api_path = self._process_params(f'coins/{id}/status_updates', params)
        return self._request('GET', api_path)

    def get_coin_ohlc(self,
                      id: str,
                      vs_currency: str,
                      days: Union[int, str],
                      params: Optional[Dict[str, Any]] = None) -> List[list]:
        """Get coin's OHLC (candles)."""
        _params = {'vs_currency': vs_currency, 'days': days}
        if params:
            _params.update(params)
        api_path = self._process_params(f'coins/{id}/ohlc', _params)
        return self._request('GET', api_path)

    # contract
    def get_token_info(self,
                       id: str,
                       contract_address: str,
                       params: Optional[Dict[str, Any]] = None) -> dict:
        """Get coin info from contract address."""
        api_path = self._process_params(
            f'coins/{id}/contract/{contract_address}', params)
        return self._request('GET', api_path)

    def get_token_market_chart(
            self,
            id: str,
            contract_address: str,
            vs_currency: str,
            days: Union[int, str],
            params: Optional[Dict[str, Any]] = None) -> dict:
        """Get historical market data for a token."""
        _params = {'vs_currency': vs_currency, 'days': days}
        if params:
            _params.update(params)
        api_path = self._process_params(
            f'coins/{id}/contract/{contract_address}/market_chart', _params)
        return self._request('GET', api_path)

    def get_token_market_chart_range(
            self,
            id: str,
            contract_address: str,
            vs_currency: str,
            from_unix_ts: int,
            to_unix_ts: int,
            params: Optional[Dict[str, Any]] = None) -> dict:
        """Get historical market data within a range of time for a token."""
        if from_unix_ts > to_unix_ts:
            raise ValueError('from_unix_tx should be smaller than to_unix_ts.')

        _params = {
            'vs_currency': vs_currency,
            'from': from_unix_ts,
            'to': to_unix_ts
        }
        if params:
            _params.update(params)
        api_path = self._process_params(
            f'coins/{id}/contract/{contract_address}/market_chart/range',
            _params)
        return self._request('GET', api_path)

    # asset platforms
    def list_asset_platforms(self) -> List[dict]:
        """List all asset platforms."""
        return self._request('GET', 'asset_platforms')

    # categories
    def list_coins_categories(self) -> List[dict]:
        """List all categories of coins."""
        return self._request('GET', '/coins/categories/list')

    def list_coins_categories_market(self,
                                     params: Optional[Dict[str, Any]] = None
                                     ) -> List[dict]:
        """List all categories of coins with market data."""
        api_path = self._process_params('/coins/categories', params)
        return self._request('GET', api_path)
