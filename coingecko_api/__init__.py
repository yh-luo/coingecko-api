import atexit
from typing import Any, Dict, List, Optional, Union

from requests import Request, Response, Session

__version__ = '0.1.0'


def _check_params(params):
    if params is not None and type(params) != dict:
        raise ValueError(('params should be a dict object, e.g.,'
                          "{'order': 'market_cap_desc'}"))


class CoinGeckoAPI:
    """Wrapper for CoinGecko API (V3).

    Args:
        **kwargs: additional keyword arguments to pass in `requests.Request`.

    Attributes:
        kwargs: additional keyword arguments to pass in `requests.Request`.
        session: current `requests.Session` connection.

    """
    _ENDPOINT = 'https://api.coingecko.com/api/v3/'
    _CONNECT_TIMEOUT_S = 5

    def __init__(self, **kwargs) -> None:
        self.kwargs = kwargs
        self.session = Session()
        atexit.register(self.close)

    def __del__(self) -> None:
        self.close()

    def _request(self,
                 path: str,
                 method: str = 'GET',
                 params: Union[dict, None] = None) -> Any:
        request = Request(method=method,
                          url=self._ENDPOINT + path,
                          params=params,
                          **self.kwargs)
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

    def close(self) -> None:
        """Make sure the connection is closed."""
        if self.session is not None:
            self.session.close()

    #
    # ping
    #
    def ping(self) -> dict:
        """Check API server status."""
        return self._request('ping')

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

        return self._request('simple/price', params=_params)

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

        return self._request(f'simple/token_price/{id}', params=_params)

    def get_supported_vs_currencies(self) -> List[str]:
        """Get list of supported vs_currencies."""
        return self._request('simple/supported_vs_currencies')

    #
    # coins
    #
    def list_coins(self) -> List[dict]:
        """List all supported coins (no pagination required)."""
        return self._request('coins/list')

    def list_coins_markets(
            self,
            vs_currency: str,
            params: Optional[Dict[str, Any]] = None) -> List[dict]:
        """List all supported coins price and market related data."""
        _params = {'vs_currency': vs_currency}
        if params:
            _check_params(params)
            _params.update(params)

        return self._request('coins/markets', params=_params)

    def get_coin(self,
                 id: str,
                 params: Optional[Dict[str, Any]] = None) -> dict:
        """Get current data for a coin."""
        return self._request(f'coins/{id}', params=params)

    def get_coin_tickers(self,
                         id: str,
                         params: Optional[Dict[str, Any]] = None) -> dict:
        """Get coin tickers (paginated to 100 items)."""
        return self._request(f'coins/{id}/tickers', params=params)

    def get_coin_history(self,
                         id: str,
                         date: str,
                         params: Optional[Dict[str, Any]] = None) -> dict:
        """Get historical data at a given date for a coin."""
        _params = {'date': date}
        if params:
            _check_params(params)
            _params.update(params)

        return self._request(f'coins/{id}/history', params=_params)

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

        return self._request(f'coins/{id}/market_chart', params=_params)

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

        return self._request(f'coins/{id}/market_chart/range', params=_params)

    def get_coin_status(self,
                        id: str,
                        params: Optional[Dict[str, Any]] = None) -> dict:
        """Get status updates for a given coin."""

        return self._request(f'coins/{id}/status_updates', params=params)

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

        return self._request(f'coins/{id}/ohlc', params=_params)

    #
    # contract/token
    #
    def get_token_info(self,
                       id: str,
                       contract_address: str,
                       params: Optional[Dict[str, Any]] = None) -> dict:
        """Get coin info from contract address."""
        return self._request(f'coins/{id}/contract/{contract_address}',
                             params=params)

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

        return self._request(
            f'coins/{id}/contract/{contract_address}/market_chart',
            params=_params)

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

        return self._request(
            f'coins/{id}/contract/{contract_address}/market_chart/range',
            params=_params)

    #
    # asset platforms
    #
    def list_asset_platforms(self) -> List[dict]:
        """List all asset platforms."""
        return self._request('asset_platforms')

    #
    # categories
    #
    def list_coins_categories(self) -> List[dict]:
        """List all categories of coins."""
        return self._request('coins/categories/list')

    def list_coins_categories_market(self,
                                     params: Optional[Dict[str, Any]] = None
                                     ) -> List[dict]:
        """List all categories of coins with market data."""

        return self._request('coins/categories', params=params)

    #
    # exchanges
    #
    def list_exchanges_info(self,
                            params: Optional[Dict[str,
                                                  Any]] = None) -> List[dict]:
        """List all exchanges with available information."""

        return self._request('exchanges', params=params)

    def list_exchanges(self) -> List[dict]:
        """List all supported markets id and name (no pagination)."""
        return self._request('exchanges/list')

    def get_exchange_volume(self, id: str) -> dict:
        """Get exchange volume in BTC and top 100 tickers only"""
        return self._request(f'exchanges/{id}')

    def get_exchange_tickers(self,
                             id: str,
                             params: Optional[Dict[str, Any]] = None) -> dict:
        """Get exchange tickers (paginated)."""

        return self._request(f'exchanges/{id}/tickers', params=params)

    def get_exchange_status(self,
                            id: str,
                            params: Optional[Dict[str, Any]] = None) -> dict:
        """Get status updates for a given exchange."""
        return self._request(f'exchanges/{id}/status_updates', params=params)

    def get_exchange_volume_chart(self, id: str, days: int) -> List[list]:
        """Get volume_chart data for a given exchange."""

        return self._request(f'exchanges/{id}/volume_chart',
                             params={'days': days})

    #
    # finance
    #
    def list_finance_platforms(self,
                               params: Optional[Dict[str, Any]] = None
                               ) -> List[dict]:
        """List all finance platforms."""

        return self._request('finance_platforms', params=params)

    def list_finance_products(self,
                              params: Optional[Dict[str, Any]] = None
                              ) -> List[dict]:

        return self._request('finance_products', params=params)

    #
    # indexes
    #
    def list_indexes_info(self,
                          params: Optional[Dict[str,
                                                Any]] = None) -> List[dict]:
        """List all market indexes with available information."""

        return self._request('indexes', params=params)

    def list_indexes(self) -> List[dict]:
        """List market indexes id and name."""
        return self._request('indexes/list')

    # NOTE: unable to test
    def get_market_index(self, market_id: str, id: str) -> dict:
        """Get market index by market id and index id."""
        return self._request(f'indexes/{market_id}/{id}')

    #
    # derivatives
    #
    def list_derivatives(self,
                         params: Optional[Dict[str,
                                               Any]] = None) -> List[dict]:
        """List all derivative tickers."""

        return self._request('derivatives', params=params)

    def list_derivatives_exchanges_info(self,
                                        params: Optional[Dict[str, Any]] = None
                                        ) -> List[dict]:
        """List all derivative exchanges with available information."""

        return self._request('derivatives/exchanges', params=params)

    def get_derivatives_exchange_info(self,
                                      id: str,
                                      params: Optional[Dict[str, Any]] = None
                                      ) -> dict:
        """Get derivative exchange data (able to include tickers)."""

        return self._request(f'derivatives/exchanges/{id}', params=params)

    def list_derivatives_exchanges(self) -> List[dict]:
        return self._request('derivatives/exchanges/list')

    #
    # status_updates
    #
    def get_status_updates(self,
                           params: Optional[Dict[str, Any]] = None) -> dict:
        """List all status_updates with data."""

        return self._request('status_updates', params=params)

    #
    # events
    #
    def list_events(self, params: Optional[Dict[str, Any]] = None) -> dict:
        """Get events, paginated by 100."""

        return self._request('events', params=params)

    def list_event_countries(self) -> dict:
        """Get list of event countries."""
        return self._request('events/countries')

    def list_event_types(self) -> dict:
        """Get list of event types."""
        return self._request('events/types')

    #
    # global
    #
    def get_global(self) -> dict:
        """Get cryptocurrency global data."""
        return self._request('global')

    def get_global_defi(self) -> dict:
        """Get top 100 cryptocurrency decentralized finance(defi) data."""
        return self._request('global/decentralized_finance_defi')

    #
    # exchange_rates
    #
    def get_exchange_rates(self) -> dict:
        """Get BTC-to-Currency exchange rates."""
        return self._request('exchange_rates')

    #
    # trending
    #
    def get_search_trending(self) -> dict:
        """Get trending search coins (Top7) in the last 24 hours."""
        return self._request('search/trending')

    #
    # companies
    #
    def list_companies_holdings(self, id: str) -> dict:
        """Get public companies bitcoin or ethereum holdings. (beta)"""
        return self._request(f'companies/public_treasury/{id}')
