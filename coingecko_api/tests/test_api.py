import pytest
import responses
from coingecko_api import CoinGeckoAPI
from requests.exceptions import HTTPError

END_POINTS = 'https://api.coingecko.com/api/v3/'
TEST_RESP = [{"id": "bitcoin", "symbol": "btc", "name": "Bitcoin"}]

cg = CoinGeckoAPI()


class TestAPI:
    @responses.activate
    def test_ping(self):
        """Test /ping."""
        resp_json = {'gecko_says': '(V3) To the Moon!'}
        responses.add(responses.GET,
                      END_POINTS + 'ping',
                      json=resp_json,
                      status=200)

        response = cg.ping()

        assert response == resp_json

    @responses.activate
    def test_get_simple_price(self):
        """Test /simple/price."""
        resp_json_s = {"bitcoin": {"usd": 50087}}
        resp_json_l = {
            "bitcoin": {
                "usd": 50087,
                "jpy": 5571067
            },
            "ethereum": {
                "usd": 3453.26,
                "jpy": 384063
            }
        }
        # str
        responses.add(responses.GET,
                      END_POINTS +
                      'simple/price?ids=bitcoin&vs_currencies=usd',
                      json=resp_json_s,
                      status=200)
        response_s = cg.get_simple_price('bitcoin', 'usd')
        assert response_s == resp_json_s

        # list
        responses.add(
            responses.GET,
            END_POINTS +
            'simple/price?ids=bitcoin%2Cethereum&vs_currencies=usd%2Cjpy',
            json=resp_json_l,
            status=200)
        response_l = cg.get_simple_price(['bitcoin', 'ethereum'],
                                         ['usd', 'jpy'])
        assert response_l == resp_json_l

    @responses.activate
    def test_get_simple_token_price(self):
        contract_addresses_s = '0xdac17f958d2ee523a2206206994597c13d831ec7'
        contract_addresses_l = [
            '0xdac17f958d2ee523a2206206994597c13d831ec7',
            '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48'
        ]
        vs_currencies_s = 'usd'
        vs_currencies_l = ['usd', 'jpy']
        resp_json_s = {
            "0xdac17f958d2ee523a2206206994597c13d831ec7": {
                "usd": 1
            }
        }
        resp_json_l = {
            "0xdac17f958d2ee523a2206206994597c13d831ec7": {
                "usd": 1,
                "jpy": 111.58
            },
            "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48": {
                "usd": 1,
                "jpy": 111.66
            }
        }
        # str
        responses.add(responses.GET,
                      END_POINTS +
                      ('simple/token_price/ethereum'
                       f'?contract_addresses={contract_addresses_s}'
                       f'&vs_currencies={vs_currencies_s}'),
                      json=resp_json_s,
                      status=200)
        response_s = cg.get_simple_token_price('ethereum',
                                               contract_addresses_s,
                                               vs_currencies_s)
        assert response_s == resp_json_s

        # list
        responses.add(responses.GET,
                      END_POINTS +
                      ('simple/token_price/ethereum'
                       f'?contract_addresses={contract_addresses_l[0]}'
                       f'%2C{contract_addresses_l[1]}'
                       f'&vs_currencies={vs_currencies_l[0]}'
                       f'%2C{vs_currencies_l[1]}'),
                      json=resp_json_l,
                      status=200)
        response_l = cg.get_simple_token_price('ethereum',
                                               contract_addresses_l,
                                               vs_currencies_l)
        assert response_l == resp_json_l

    @responses.activate
    def test_get_supported_vs_currencies(self):
        """Test /simple/supported_vs_currencies."""
        resp_json = ['btc', 'eth']
        responses.add(responses.GET,
                      END_POINTS + 'simple/supported_vs_currencies',
                      json=resp_json,
                      status=200)

        response = cg.get_supported_vs_currencies()
        assert response == resp_json

    @responses.activate
    def test_failed_ping(self):
        """Test /ping 404."""
        responses.add(responses.GET, END_POINTS + 'ping', status=404)

        with pytest.raises(HTTPError):
            cg.ping()

    @responses.activate
    def test_list_coins(self):
        """Test /coins/list."""
        responses.add(responses.GET,
                      END_POINTS + 'coins/list',
                      json=TEST_RESP,
                      status=200)
        response = cg.list_coins()

        assert response == TEST_RESP

    @responses.activate
    def test_list_coins_markets(self):
        """Test /coins/markets."""
        responses.add(responses.GET,
                      END_POINTS + 'coins/markets?vs_currency=bitcoin',
                      json=TEST_RESP,
                      status=200)
        response = cg.list_coins_markets('bitcoin')

        assert response == TEST_RESP

    @responses.activate
    def test_get_coin(self):
        """Test /coins/{id}."""
        responses.add(responses.GET,
                      END_POINTS + 'coins/bitcoin',
                      json=TEST_RESP[0],
                      status=200)
        response = cg.get_coin('bitcoin')

        assert response == TEST_RESP[0]

    @responses.activate
    def test_get_coin_tickers(self):
        """Test /coins/{id}/tickers."""
        resp_json = {
            "name":
            "Bitcoin",
            "tickers": [{
                "base": "BTC",
                "target": "USD",
                "market": {
                    "name": "Bitfinex",
                    "identifier": "bitfinex",
                    "has_trading_incentive": "false"
                }
            }]
        }
        responses.add(responses.GET,
                      END_POINTS + 'coins/bitcoin/tickers',
                      json=resp_json,
                      status=200)
        response = cg.get_coin_tickers('bitcoin')

        assert response == resp_json

    @responses.activate
    def test_get_coin_history(self):
        """Test /coins/{id}/history."""
        date = '01-10-2021'
        resp_json = {
            "id": "bitcoin",
            "symbol": "btc",
            "name": "Bitcoin",
            "localization": {
                "en": "Bitcoin",
                "id": "Bitcoin"
            },
            "market_data": {
                "current_price": {
                    "btc": 1,
                    "usd": 43859.32614724109,
                },
                "market_cap": {
                    "btc": 18830918,
                    "usd": 827840965059.6127
                }
            }
        }
        responses.add(responses.GET,
                      END_POINTS + 'coins/bitcoin/history?date=' + date,
                      json=resp_json,
                      status=200)
        response = cg.get_coin_history('bitcoin', date=date)

        assert response == resp_json

    @responses.activate
    def test_get_coin_market_chart(self):
        """Test /coins/{id}/market_chart."""
        resp_json = {
            "prices": [[1633347897116, 47470.985980739715]],
            "market_caps": [[1633347897116, 897002925893.1621]],
            "total_volumes": [[1633347897116, 25853740745.60097]]
        }
        responses.add(responses.GET,
                      END_POINTS +
                      'coins/bitcoin/market_chart?vs_currency=usd&days=1',
                      json=resp_json,
                      status=200)
        response = cg.get_coin_market_chart('bitcoin', 'usd', 1)

        assert response == resp_json

    @responses.activate
    def test_get_coin_market_chart_range(self):
        """Test /coins/{id}/market_chart/range."""
        from_unix_ts = 1392577232
        to_unix_ts = 1422577232
        resp_json = {
            "prices": [[1392595200000, 645.14]],
            "market_caps": [[1392595200000, 8005429360]],
            "total_volumes": [[1392595200000, 48516100]]
        }
        responses.add(responses.GET,
                      END_POINTS +
                      f'coins/bitcoin/market_chart/range?vs_currency=usd' +
                      f'&from={from_unix_ts}&to={to_unix_ts}',
                      json=resp_json,
                      status=200)
        response = cg.get_coin_market_chart_range('bitcoin', 'usd',
                                                  from_unix_ts, to_unix_ts)

        assert response == resp_json

        with pytest.raises(ValueError, match=r'.*from_unix_tx.*to_unix_ts.*'):
            cg.get_coin_market_chart_range('bitcoin',
                                           'usd',
                                           from_unix_ts=to_unix_ts,
                                           to_unix_ts=from_unix_ts)

    @responses.activate
    def test_get_coin_status(self):
        """Test /coins/{id}/status_updates."""
        resp_json = {"status_updates": []}
        responses.add(responses.GET,
                      END_POINTS + f'coins/bitcoin/status_updates',
                      json=resp_json,
                      status=200)
        response = cg.get_coin_status('bitcoin')

        assert response == resp_json

    @responses.activate
    def test_get_coin_ohlc(self):
        """Test /coins/{id}/ohlc."""
        resp_json = [[1633350600000, 47901.63, 47901.63, 47845.59, 47845.59]]
        responses.add(responses.GET,
                      END_POINTS +
                      f'coins/bitcoin/ohlc?vs_currency=usd&days=1',
                      json=resp_json,
                      status=200)
        response = cg.get_coin_ohlc('bitcoin', 'usd', 1)

        assert response == resp_json

    # contract
    @responses.activate
    def test_get_token_info(self):
        """Test /coins/{id}/contract/{contract_address}."""
        contract_address = '0xdac17f958d2ee523a2206206994597c13d831ec7'
        resp_json = {
            "id": "tether",
            "symbol": "usdt",
            "name": "Tether",
            "asset_platform_id": "ethereum",
            "platforms": {
                "ethereum": "0xdac17f958d2ee523a2206206994597c13d831ec7",
                "binance-smart-chain":
                "0x55d398326f99059ff775485246999027b3197955"
            }
        }
        responses.add(responses.GET,
                      END_POINTS +
                      f'coins/ethereum/contract/{contract_address}',
                      json=resp_json,
                      status=200)
        response = cg.get_token_info('ethereum', contract_address)

        assert response == resp_json

    @responses.activate
    def test_get_token_market_chart(self):
        """Test /coins/{id}/contract/{contract_address}/market_chart."""
        contract_address = '0xdac17f958d2ee523a2206206994597c13d831ec7'
        resp_json = {
            "prices": [[1633366855116, 0.9999874659209217]],
            "market_caps": [[1633366855116, 68765623234.10846]],
            "total_volumes": [[1633366855116, 65421865374.78419]]
        }
        responses.add(responses.GET,
                      END_POINTS +
                      (f'coins/ethereum/contract/{contract_address}/'
                       'market_chart?vs_currency=usd&days=1'),
                      json=resp_json,
                      status=200)
        response = cg.get_token_market_chart('ethereum', contract_address,
                                             'usd', 1)
        assert response == resp_json

    @responses.activate
    def test_get_token_market_chart_range(self):
        """Test /coins/{id}/contract/{contract_address}/market_chart/range."""
        contract_address = '0xdac17f958d2ee523a2206206994597c13d831ec7'
        from_unix_ts = 1422577232
        to_unix_ts = 1426577232
        resp_json = {
            "prices": [[1424822400000, 1.21016]],
            "market_caps": [
                [1424822400000, 304476],
            ],
            "total_volumes": [
                [1424822400000, 5],
            ]
        }
        responses.add(responses.GET,
                      END_POINTS +
                      (f'coins/ethereum/contract/{contract_address}/'
                       'market_chart/range?vs_currency=usd'
                       f'&from={from_unix_ts}&to={to_unix_ts}'),
                      json=resp_json,
                      status=200)
        response = cg.get_token_market_chart_range('ethereum',
                                                   contract_address, 'usd',
                                                   from_unix_ts, to_unix_ts)
        assert response == resp_json
