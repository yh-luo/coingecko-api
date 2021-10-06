import pytest
import responses
from coingecko_api import CoinGeckoAPI
from requests.exceptions import HTTPError

END_POINTS = 'https://api.coingecko.com/api/v3/'

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
        id = 'ethereum'
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
                      (f'simple/token_price/{id}'
                       f'?contract_addresses={contract_addresses_s}'
                       f'&vs_currencies={vs_currencies_s}'),
                      json=resp_json_s,
                      status=200)
        response_s = cg.get_simple_token_price(id, contract_addresses_s,
                                               vs_currencies_s)
        assert response_s == resp_json_s

        # list
        responses.add(responses.GET,
                      END_POINTS +
                      (f'simple/token_price/{id}'
                       f'?contract_addresses={contract_addresses_l[0]}'
                       f'%2C{contract_addresses_l[1]}'
                       f'&vs_currencies={vs_currencies_l[0]}'
                       f'%2C{vs_currencies_l[1]}'),
                      json=resp_json_l,
                      status=200)
        response_l = cg.get_simple_token_price(id, contract_addresses_l,
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
        resp_json = [{"id": "bitcoin", "symbol": "btc", "name": "Bitcoin"}]
        responses.add(responses.GET,
                      END_POINTS + 'coins/list',
                      json=resp_json,
                      status=200)
        response = cg.list_coins()

        assert response == resp_json

    @responses.activate
    def test_list_coins_markets(self):
        """Test /coins/markets."""
        id = 'bitcoin'
        resp_json = [{"id": "bitcoin", "symbol": "btc", "name": "Bitcoin"}]
        responses.add(responses.GET,
                      END_POINTS + 'coins/markets?vs_currency=bitcoin',
                      json=resp_json,
                      status=200)
        response = cg.list_coins_markets(id)

        assert response == resp_json

    @responses.activate
    def test_get_coin(self):
        """Test /coins/{id}."""
        id = 'bitcoin'
        resp_json = {"id": "bitcoin", "symbol": "btc", "name": "Bitcoin"}
        responses.add(responses.GET,
                      END_POINTS + 'coins/bitcoin',
                      json=resp_json,
                      status=200)
        response = cg.get_coin(id)

        assert response == resp_json

    @responses.activate
    def test_get_coin_tickers(self):
        """Test /coins/{id}/tickers."""
        id = 'bitcoin'
        resp_json = {
            "name": "Bitcoin",
            "tickers": [{
                "base": "BTC",
                "target": "USD"
            }]
        }
        responses.add(responses.GET,
                      END_POINTS + f'coins/{id}/tickers',
                      json=resp_json,
                      status=200)
        response = cg.get_coin_tickers(id)

        assert response == resp_json

    @responses.activate
    def test_get_coin_history(self):
        """Test /coins/{id}/history."""
        id = 'bitcoin'
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
                      END_POINTS + f'coins/{id}/history?date={date}',
                      json=resp_json,
                      status=200)
        response = cg.get_coin_history(id, date)

        assert response == resp_json

    @responses.activate
    def test_get_coin_market_chart(self):
        """Test /coins/{id}/market_chart."""
        id = 'bitcoin'
        vs_currency = 'usd'
        days = 1
        resp_json = {
            "prices": [[1633347897116, 47470.985980739715]],
            "market_caps": [[1633347897116, 897002925893.1621]],
            "total_volumes": [[1633347897116, 25853740745.60097]]
        }
        responses.add(
            responses.GET,
            END_POINTS +
            f'coins/{id}/market_chart?vs_currency={vs_currency}&days={days}',
            json=resp_json,
            status=200)
        response = cg.get_coin_market_chart(id, vs_currency, days)

        assert response == resp_json

    @responses.activate
    def test_get_coin_market_chart_range(self):
        """Test /coins/{id}/market_chart/range."""
        id = 'bitcoin'
        vs_currency = 'usd'
        from_unix_ts = 1392577232
        to_unix_ts = 1422577232
        resp_json = {
            "prices": [[1392595200000, 645.14]],
            "market_caps": [[1392595200000, 8005429360]],
            "total_volumes": [[1392595200000, 48516100]]
        }
        responses.add(
            responses.GET,
            END_POINTS +
            (f'coins/{id}/market_chart/range?vs_currency={vs_currency}'
             f'&from={from_unix_ts}&to={to_unix_ts}'),
            json=resp_json,
            status=200)
        response = cg.get_coin_market_chart_range(id, vs_currency,
                                                  from_unix_ts, to_unix_ts)

        assert response == resp_json

        with pytest.raises(ValueError, match=r'.*from_unix_tx.*to_unix_ts.*'):
            cg.get_coin_market_chart_range(id,
                                           vs_currency,
                                           from_unix_ts=to_unix_ts,
                                           to_unix_ts=from_unix_ts)

    @responses.activate
    def test_get_coin_status(self):
        """Test /coins/{id}/status_updates."""
        id = 'bitcoin'
        resp_json = {"status_updates": []}
        responses.add(responses.GET,
                      END_POINTS + f'coins/{id}/status_updates',
                      json=resp_json,
                      status=200)
        response = cg.get_coin_status(id)

        assert response == resp_json

    @responses.activate
    def test_get_coin_ohlc(self):
        """Test /coins/{id}/ohlc."""
        id = 'bitcoin'
        vs_currency = 'usd'
        days = 1
        resp_json = [[1633350600000, 47901.63, 47901.63, 47845.59, 47845.59]]
        responses.add(responses.GET,
                      END_POINTS +
                      f'coins/{id}/ohlc?vs_currency={vs_currency}&days={days}',
                      json=resp_json,
                      status=200)
        response = cg.get_coin_ohlc(id, vs_currency, days)

        assert response == resp_json

    # contract
    @responses.activate
    def test_get_token_info(self):
        """Test /coins/{id}/contract/{contract_address}."""
        id = 'ethereum'
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
                      END_POINTS + f'coins/{id}/contract/{contract_address}',
                      json=resp_json,
                      status=200)
        response = cg.get_token_info(id, contract_address)

        assert response == resp_json

    @responses.activate
    def test_get_token_market_chart(self):
        """Test /coins/{id}/contract/{contract_address}/market_chart."""
        id = 'ethereum'
        vs_currency = 'usd'
        days = 1
        contract_address = '0xdac17f958d2ee523a2206206994597c13d831ec7'
        resp_json = {
            "prices": [[1633366855116, 0.9999874659209217]],
            "market_caps": [[1633366855116, 68765623234.10846]],
            "total_volumes": [[1633366855116, 65421865374.78419]]
        }
        responses.add(responses.GET,
                      END_POINTS +
                      (f'coins/{id}/contract/{contract_address}/'
                       f'market_chart?vs_currency={vs_currency}&days={days}'),
                      json=resp_json,
                      status=200)
        response = cg.get_token_market_chart(id, contract_address, vs_currency,
                                             days)
        assert response == resp_json

    @responses.activate
    def test_get_token_market_chart_range(self):
        """Test /coins/{id}/contract/{contract_address}/market_chart/range."""
        id = 'ethereum'
        vs_currency = 'usd'
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
                      (f'coins/{id}/contract/{contract_address}/'
                       f'market_chart/range?vs_currency={vs_currency}'
                       f'&from={from_unix_ts}&to={to_unix_ts}'),
                      json=resp_json,
                      status=200)
        response = cg.get_token_market_chart_range(id, contract_address,
                                                   vs_currency, from_unix_ts,
                                                   to_unix_ts)
        assert response == resp_json

    # asset_platforms
    @responses.activate
    def test_list_asset_platforms(self):
        """Test /asset_platforms."""
        resp_json = [{
            "id": "ethereum",
            "chain_identifier": 1,
            "name": "ethereum"
        }]
        responses.add(responses.GET,
                      END_POINTS + 'asset_platforms',
                      json=resp_json,
                      status=200)
        response = cg.list_asset_platforms()
        assert response == resp_json

    # categories
    @responses.activate
    def test_list_coins_categories(self):
        """Test /coins/categories/list."""
        resp_json = [{"category_id": "stablecoins", "name": "Stablecoins"}]
        responses.add(responses.GET,
                      END_POINTS + 'coins/categories/list',
                      json=resp_json,
                      status=200)
        response = cg.list_coins_categories()
        assert response == resp_json

    @responses.activate
    def test_list_coins_categories_market(self):
        """Test /coins/categories."""
        resp_json = [{
            "id": "stablecoins",
            "name": "Stablecoins",
            "market_cap": 130789992686.07925,
            "market_cap_change_24h": 0.3863018764023684,
            "volume_24h": 80474506243.29338,
            "updated_at": "2021-10-05T17:40:26.143Z"
        }]
        responses.add(responses.GET,
                      END_POINTS + 'coins/categories',
                      json=resp_json,
                      status=200)
        response = cg.list_coins_categories_market()
        assert response == resp_json

    @responses.activate
    def test_list_exchanges_info(self):
        """Test /exchanges."""
        resp_json = [{
            "id": "binance",
            "name": "Binance",
            "year_established": 2017,
            "url": "https://www.binance.com/"
        }]
        responses.add(responses.GET,
                      END_POINTS + 'exchanges',
                      json=resp_json,
                      status=200)
        response = cg.list_exchanges_info()
        assert response == resp_json

    @responses.activate
    def test_list_exchanges(self):
        """Test /exchanges/list."""
        resp_json = [{"id": "aave", "name": "Aave"}]
        responses.add(responses.GET,
                      END_POINTS + 'exchanges/list',
                      json=resp_json,
                      status=200)
        response = cg.list_exchanges()
        assert response == resp_json

    @responses.activate
    def test_get_exchange_volume(self):
        """Test exchanges/{id}."""
        id = 'binance'
        resp_json = {
            "name":
            "Binance",
            "trade_volume_24h_btc":
            543589.4534134716,
            "trade_volume_24h_btc_normalized":
            543589.4534134716,
            "tickers": [{
                "base": "BTC",
                "target": "USDT",
                "market": {
                    "name": "Binance",
                    "identifier": "binance",
                    "has_trading_incentive": "false"
                },
                "last": 51437.01,
                "volume": 50301.077907601284,
                "converted_last": {
                    "btc": 1.001974,
                    "eth": 14.70506,
                    "usd": 51503
                },
                "converted_volume": {
                    "btc": 50400,
                    "eth": 739680,
                    "usd": 2590658746
                }
            }]
        }
        responses.add(responses.GET,
                      END_POINTS + f'exchanges/{id}',
                      json=resp_json,
                      status=200)
        response = cg.get_exchange_volume(id)

        assert response == resp_json

    @responses.activate
    def test_get_exchange_tickers(self):
        """Test /exchanges/{id}/tickers."""
        id = 'binance'
        resp_json = {
            "name":
            "Binance",
            "tickers": [{
                "base": "BTC",
                "target": "USDT",
                "market": {
                    "name": "Binance",
                    "identifier": "binance",
                    "has_trading_incentive": "false"
                },
                "last": 51534.03,
                "volume": 50514.87895281648,
                "converted_last": {
                    "btc": 0.99958898,
                    "eth": 14.704929,
                    "usd": 51593
                },
                "converted_volume": {
                    "btc": 50494,
                    "eth": 742818,
                    "usd": 2606201489
                },
                "coin_id": "bitcoin",
                "target_coin_id": "tether"
            }]
        }
        responses.add(responses.GET,
                      END_POINTS + f'exchanges/{id}/tickers',
                      json=resp_json,
                      status=200)
        response = cg.get_exchange_tickers(id)

        assert response == resp_json

    @responses.activate
    def test_get_exchange_status(self):
        """Test /exchanges/{id}/status_updates."""
        id = 'binance'
        resp_json = {
            "status_updates": [{
                "description": "Binance Launchpool",
                "category": "general",
                "created_at": "2020-12-14T11:18:49.085Z",
                "user": "Darc",
                "user_title": "Marketing"
            }]
        }
        responses.add(responses.GET,
                      END_POINTS + f'exchanges/{id}/status_updates',
                      json=resp_json,
                      status=200)
        response = cg.get_exchange_status(id)

        assert response == resp_json

    @responses.activate
    def test_get_exchange_volume_chart(self):
        """Test /exchanges/{id}/volume_chart"""
        id = 'binance'
        days = 1
        resp_json = [[1633408200000, "540716.62953207615878112376190664116"],
                     [1633408800000, "539567.02347984278641005250981327051"]]
        responses.add(responses.GET,
                      END_POINTS + f'exchanges/{id}/volume_chart',
                      json=resp_json,
                      status=200)
        response = cg.get_exchange_volume_chart(id, days)

        assert response == resp_json

    @responses.activate
    def test_list_finance_platforms(self):
        """Test /finance_platforms."""
        resp_json = [{
            "name": "Aave",
            "category": "DeFi Platform",
            "centralized": "false",
            "website_url": "https://aave.com/"
        }]
        responses.add(responses.GET,
                      END_POINTS + 'finance_platforms',
                      json=resp_json,
                      status=200)
        response = cg.list_finance_platforms()

        assert response == resp_json

    @responses.activate
    def test_list_finance_products(self):
        """Test /finance_platforms."""
        resp_json = [{"platform": "Celsius Network", "identifier": "USDC"}]
        responses.add(responses.GET,
                      END_POINTS + 'finance_products',
                      json=resp_json,
                      status=200)
        response = cg.list_finance_products()

        assert response == resp_json