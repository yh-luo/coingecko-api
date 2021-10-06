import atexit
from typing import Any, Dict, List, Optional, Union

from requests import Request, Response, Session

__version__ = '0.1.0'


def _check_params(params):
    if params is not None and type(params) != dict:
        raise ValueError(('params should be a dict object, e.g.,'
                          "{'order': 'market_cap_desc'}"))


class CoinGeckoAPI:
    _ENDPOINT = 'https://api.coingecko.com/api/v3/'
    _CONNECT_TIMEOUT_S = 5

    def __init__(self) -> None:
        self.session = Session()
        atexit.register(self.close)

    def __del__(self):
        self.close()

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
                        params: Optional[Dict[str, Any]] = None) -> str:
        if params:
            _check_params(params)
            api_path += '?'
            for key, val in params.items():
                if type(val) == bool:
                    val = str(val).lower()
                api_path += f'{key}={val}&'
            api_path = api_path[:-1]  # remove the redundant '&'
        return api_path

    def close(self):
        """Make sure the connection is closed."""
        if self.session is not None:
            self.session.close()

    # ping
    def ping(self) -> dict:
        """Check API server status."""
        return self._request('GET', 'ping')

    #
    # simple
    #
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
            _check_params(params)
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
            _check_params(params)
            _params.update(params)
        api_path = self._process_params(f'simple/token_price/{id}', _params)
        return self._request('GET', api_path)

    def get_supported_vs_currencies(self) -> List[str]:
        """Get list of supported vs_currencies."""
        return self._request('GET', 'simple/supported_vs_currencies')

    #
    # coins
    #
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
            _check_params(params)
            _params.update(params)
        api_path = self._process_params('coins/markets', _params)
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
            _check_params(params)
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
            _check_params(params)
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
            _check_params(params)
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
            _check_params(params)
            _params.update(params)
        api_path = self._process_params(f'coins/{id}/ohlc', _params)
        return self._request('GET', api_path)

    #
    # contract/token
    #
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
            _check_params(params)
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
            _check_params(params)
            _params.update(params)
        api_path = self._process_params(
            f'coins/{id}/contract/{contract_address}/market_chart/range',
            _params)
        return self._request('GET', api_path)

    #
    # asset platforms
    #
    def list_asset_platforms(self) -> List[dict]:
        """List all asset platforms."""
        return self._request('GET', 'asset_platforms')

    #
    # categories
    #
    def list_coins_categories(self) -> List[dict]:
        """List all categories of coins."""
        return self._request('GET', 'coins/categories/list')

    def list_coins_categories_market(self,
                                     params: Optional[Dict[str, Any]] = None
                                     ) -> List[dict]:
        """List all categories of coins with market data."""
        api_path = self._process_params('coins/categories', params)
        return self._request('GET', api_path)

    #
    # exchanges
    #
    def list_exchanges_info(self,
                            params: Optional[Dict[str,
                                                  Any]] = None) -> List[dict]:
        """List all exchanges with available information."""
        api_path = self._process_params('exchanges', params)
        return self._request('GET', api_path)

    def list_exchanges(self) -> List[dict]:
        """List all supported markets id and name (no pagination)."""
        return self._request('GET', 'exchanges/list')

    def get_exchange_volume(self, id: str) -> dict:
        """Get exchange volume in BTC and top 100 tickers only"""
        return self._request('GET', f'exchanges/{id}')

    def get_exchange_tickers(self,
                             id: str,
                             params: Optional[Dict[str, Any]] = None) -> dict:
        """Get exchange tickers (paginated)."""
        api_path = self._process_params(f'exchanges/{id}/tickers', params)
        return self._request('GET', api_path)

    def get_exchange_status(self,
                            id: str,
                            params: Optional[Dict[str, Any]] = None) -> dict:
        """Get status updates for a given exchange."""
        api_path = self._process_params(f'exchanges/{id}/status_updates',
                                        params)
        return self._request('GET', api_path)

    def get_exchange_volume_chart(self, id: str, days: int) -> List[list]:
        """Get volume_chart data for a given exchange."""
        api_path = self._process_params(f'exchanges/{id}/volume_chart',
                                        {'days': days})
        return self._request('GET', api_path)

    #
    # finance
    #
    def list_finance_platforms(self,
                               params: Optional[Dict[str, Any]] = None
                               ) -> List[dict]:
        """List all finance platforms."""
        api_path = self._process_params('finance_platforms', params)
        return self._request('GET', api_path)

    def list_finance_products(self,
                              params: Optional[Dict[str, Any]] = None
                              ) -> List[dict]:
        api_path = self._process_params('finance_products', params)
        return self._request('GET', api_path)

    # indexes
    def list_indexes_info(self,
                          params: Optional[Dict[str,
                                                Any]] = None) -> List[dict]:
        """List all market indexes with available information."""
        api_path = self._process_params('indexes', params)
        return self._request('GET', api_path)

    def list_indexes(self) -> List[dict]:
        """List market indexes id and name."""
        return self._request('GET', 'indexes/list')

    # NOTE: unable to test
    def get_market_index(self, market_id: str, id: str) -> dict:
        """Get market index by market id and index id."""
        return self._request('GET', f'indexes/{market_id}/{id}')

    #
    # derivatives
    #
    def list_derivatives(self,
                         params: Optional[Dict[str,
                                               Any]] = None) -> List[dict]:
        """List all derivative tickers."""
        api_path = self._process_params('derivatives', params)
        return self._request('GET', api_path)

    def list_derivatives_exchanges_info(self,
                                        params: Optional[Dict[str, Any]] = None
                                        ) -> List[dict]:
        """List all derivative exchanges with available information."""
        api_path = self._process_params('derivatives/exchanges', params)
        return self._request('GET', api_path)

    def get_derivatives_exchange_info(self,
                                      id: str,
                                      params: Optional[Dict[str, Any]] = None
                                      ) -> dict:
        """Get derivative exchange data (able to include tickers)."""
        api_path = self._process_params(f'derivatives/exchanges/{id}', params)
        return self._request('GET', api_path)

    def list_derivatives_exchanges(self) -> List[dict]:
        return self._request('GET', 'derivatives/exchanges/list')

    #
    # status_updates
    #
    def get_status_updates(self,
                           params: Optional[Dict[str, Any]] = None) -> dict:
        """List all status_updates with data."""
        api_path = self._process_params('status_updates', params)
        return self._request('GET', api_path)

    #
    # events
    #
    def list_events(self, params: Optional[Dict[str, Any]] = None) -> dict:
        """Get events, paginated by 100."""
        api_path = self._process_params('events', params)
        return self._request('GET', api_path)

    def list_event_countries(self) -> dict:
        """Get list of event countries."""
        return self._request('GET', 'events/countries')

    def list_event_types(self) -> dict:
        """Get list of event types."""
        return self._request('GET', 'events/types')

    #
    # global
    #
    def get_global(self) -> dict:
        """Get cryptocurrency global data."""
        return self._request('GET', 'global')

    def get_global_defi(self) -> dict:
        """Get top 100 cryptocurrency decentralized finance(defi) data."""
        return self._request('GET', 'global/decentralized_finance_defi')

    #
    # exchange_rates
    #
    def get_exchange_rates(self) -> dict:
        """Get BTC-to-Currency exchange rates."""
        return self._request('GET', 'exchange_rates')

    #
    # trending
    #
    def get_search_trending(self) -> dict:
        """Get trending search coins (Top7) in the last 24 hours."""
        return self._request('GET', 'search/trending')

    #
    # companies
    #
    def list_companies_holdings(self, id: str) -> dict:
        """Get public companies bitcoin or ethereum holdings. (beta)"""
        return self._request('GET', f'companies/public_treasury/{id}')
