import pytest
import responses
from coingecko_api import CoinGeckoAPI
from requests.exceptions import HTTPError

END_POINTS = 'https://api.coingecko.com/api/v3/'

simple_test_data_1 = [
    ('bitcoin', 'usd', {
        "bitcoin": {
            "usd": 50087
        }
    }, {'ids': 'bitcoin', 'vs_currencies': 'usd'}),
    (['bitcoin', 'ethereum'], ['usd', 'jpy'], {
        "bitcoin": {
            "usd": 50087,
            "jpy": 5571067
        },
        "ethereum": {
            "usd": 3453.26,
            "jpy": 384063
        }
    }, {'ids': 'bitcoin,ethereum', 'vs_currencies':'usd,jpy'})
]

simple_test_data_2 = [
    ('0xdac17f958d2ee523a2206206994597c13d831ec7', 'usd', {
        "0xdac17f958d2ee523a2206206994597c13d831ec7": {
            "usd": 1
        }
    }, {'contract_addresses': '0xdac17f958d2ee523a2206206994597c13d831ec7','vs_currencies': 'usd'}),
    ([
        '0xdac17f958d2ee523a2206206994597c13d831ec7',
        '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48'
    ], ['usd', 'jpy'], {
        "0xdac17f958d2ee523a2206206994597c13d831ec7": {
            "usd": 1,
            "jpy": 111.58
        },
        "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48": {
            "usd": 1,
            "jpy": 111.66
        }
    }, {'contract_addresses': '0xdac17f958d2ee523a2206206994597c13d831ec7,0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48', 'vs_currencies': 'usd,jpy'})
]

cg = CoinGeckoAPI()



def test_check_params():
    """Test valid and invalid params."""
    with pytest.raises(ValueError, match=r'params should be a dict.*'):
        cg.get_simple_price('bitcoin', 'usd', ['market_cap_desc'])

#
# ping
#
@responses.activate
def test_ping():
    """Test /ping."""
    resp_json = {'gecko_says': '(V3) To the Moon!'}
    responses.add(responses.GET,
                    END_POINTS + 'ping',
                    json=resp_json,
                    status=200)

    response = cg.ping()
    assert response == resp_json

@responses.activate
def test_failed_ping():
    """Test /ping 404."""
    responses.add(responses.GET, END_POINTS + 'ping', status=404)

    with pytest.raises(HTTPError):
        cg.ping()

#
# simple
#
@pytest.mark.parametrize('ids,vs_currencies,resp_json,params',
                            simple_test_data_1,
                            ids=['str', 'list'])
@responses.activate
def test_get_simple_price(ids, vs_currencies, resp_json, params):
    """Test /simple/price."""
    responses.add(responses.GET,
                    END_POINTS + 'simple/price',
                    match=[responses.matchers.query_param_matcher(params)],
                    json=resp_json,
                    status=200)

    response = cg.get_simple_price(ids, vs_currencies)
    assert response == resp_json

@pytest.mark.parametrize('contract_addresses,vs_currencies,resp_json,params',
                            simple_test_data_2,
                            ids=['str', 'list'])
@responses.activate
def test_get_simple_token_price(contract_addresses, vs_currencies,
                                resp_json, params):
    responses.add(responses.GET,
                    END_POINTS + 'simple/token_price/ethereum',
                     match=[responses.matchers.query_param_matcher(params)],
                    json=resp_json,
                    status=200)

    response = cg.get_simple_token_price('ethereum', contract_addresses,
                                            vs_currencies)
    assert response == resp_json

@responses.activate
def test_get_supported_vs_currencies():
    """Test /simple/supported_vs_currencies."""
    resp_json = ['btc', 'eth']
    responses.add(responses.GET,
                    END_POINTS + 'simple/supported_vs_currencies',
                    json=resp_json,
                    status=200)

    response = cg.get_supported_vs_currencies()
    assert response == resp_json

#
# coins
#
@responses.activate
def test_list_coins():
    """Test /coins/list."""
    resp_json = [{"id": "bitcoin", "symbol": "btc", "name": "Bitcoin"}]
    responses.add(responses.GET,
                    END_POINTS + 'coins/list',
                    json=resp_json,
                    status=200)

    response = cg.list_coins()
    assert response == resp_json

@responses.activate
def test_list_coins_markets():
    """Test /coins/markets."""
    vs_currency = 'usd'
    resp_json = [{"id": "bitcoin", "symbol": "btc", "name": "Bitcoin"}]
    responses.add(responses.GET,
                    END_POINTS + f'coins/markets?vs_currency={vs_currency}',
                    json=resp_json,
                    status=200)

    response = cg.list_coins_markets(vs_currency)
    assert response == resp_json

@responses.activate
def test_get_coin():
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
def test_get_coin_tickers():
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
def test_get_coin_history():
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
def test_get_coin_market_chart():
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
def test_get_coin_market_chart_range():
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
def test_get_coin_status():
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
def test_get_coin_ohlc():
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

#
# contract/token
#
@responses.activate
def test_get_token_info():
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
def test_get_token_market_chart():
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
def test_get_token_market_chart_range():
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

#
# asset platforms
#
@responses.activate
def test_list_asset_platforms():
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

#
# categories
#
@responses.activate
def test_list_coins_categories():
    """Test /coins/categories/list."""
    resp_json = [{"category_id": "stablecoins", "name": "Stablecoins"}]
    responses.add(responses.GET,
                    END_POINTS + 'coins/categories/list',
                    json=resp_json,
                    status=200)

    response = cg.list_coins_categories()
    assert response == resp_json

#
# exchanges
#
@responses.activate
def test_list_coins_categories_market():
    """Test /coins/categories."""
    resp_json = [{
        "id": "stablecoins",
        "name": "Stablecoins",
        "market_cap": 130789992686.07925,
        "market_cap_change_24h": 0.3863018764023684,
        "volume_24h": 80474506243.29338
    }]
    responses.add(responses.GET,
                    END_POINTS + 'coins/categories',
                    json=resp_json,
                    status=200)

    response = cg.list_coins_categories_market()
    assert response == resp_json

@responses.activate
def test_list_exchanges_info():
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
def test_list_exchanges():
    """Test /exchanges/list."""
    resp_json = [{"id": "aave", "name": "Aave"}]
    responses.add(responses.GET,
                    END_POINTS + 'exchanges/list',
                    json=resp_json,
                    status=200)

    response = cg.list_exchanges()
    assert response == resp_json

@responses.activate
def test_get_exchange_volume():
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
def test_get_exchange_tickers():
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
def test_get_exchange_status():
    """Test /exchanges/{id}/status_updates."""
    id = 'binance'
    resp_json = {
        "status_updates": [{
            "description": "Binance Launchpool",
            "category": "general"
        }]
    }
    responses.add(responses.GET,
                    END_POINTS + f'exchanges/{id}/status_updates',
                    json=resp_json,
                    status=200)

    response = cg.get_exchange_status(id)
    assert response == resp_json

@responses.activate
def test_get_exchange_volume_chart():
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

#
# finance
#
@responses.activate
def test_list_finance_platforms():
    """Test /finance_platforms."""
    resp_json = [{"name": "Aave", "category": "DeFi Platform"}]
    responses.add(responses.GET,
                    END_POINTS + 'finance_platforms',
                    json=resp_json,
                    status=200)
    response = cg.list_finance_platforms()

    assert response == resp_json

@responses.activate
def test_list_finance_products():
    """Test /finance_platforms."""
    resp_json = [{"platform": "Celsius Network", "identifier": "USDC"}]
    responses.add(responses.GET,
                    END_POINTS + 'finance_products',
                    json=resp_json,
                    status=200)

    response = cg.list_finance_products()
    assert response == resp_json

#
# indexes
#
@responses.activate
def test_list_indexes_info():
    """Test /indexes."""
    resp_json = [{
        "name": "CoinFLEX (Futures) DFN",
        "id": "DFN",
        "market": "CoinFLEX (Futures)"
    }]
    responses.add(responses.GET,
                    END_POINTS + 'indexes',
                    json=resp_json,
                    status=200)

    response = cg.list_indexes_info()
    assert response == resp_json

@responses.activate
def test_list_indexes():
    """Test /indexes/list."""
    resp_json = [{"id": "DFN", "name": "CoinFLEX (Futures) DFN"}]
    responses.add(responses.GET,
                    END_POINTS + 'indexes/list',
                    json=resp_json,
                    status=200)

    response = cg.list_indexes()
    assert response == resp_json

#
# derivatives
#
@responses.activate
def test_list_derivatives():
    """Test /derivatives."""
    resp_json = [{
        "market": "Binance (Futures)",
        "symbol": "BTCUSDT",
        "index_id": "BTC"
    }]
    responses.add(responses.GET,
                    END_POINTS + 'derivatives',
                    json=resp_json,
                    status=200)

    response = cg.list_derivatives()
    assert response == resp_json

@responses.activate
def test_list_derivatives_exchanges_info():
    """Test /derivatives/exchanges."""
    resp_json = [{
        "name": "Binance (Futures)",
        "id": "binance_futures",
        "year_established": 2019,
        "url": "https://www.binance.com/"
    }]
    responses.add(responses.GET,
                    END_POINTS + 'derivatives/exchanges',
                    json=resp_json,
                    status=200)

    response = cg.list_derivatives_exchanges_info()
    assert response == resp_json

@responses.activate
def test_get_derivatives_exchange_info():
    """Test /derivatives/exchanges/{id}."""
    id = 'binance_futures'
    resp_json = [{
        "name": "Binance (Futures)",
        "id": "binance_futures",
        "year_established": 2019,
        "url": "https://www.binance.com/"
    }]
    responses.add(responses.GET,
                    END_POINTS + f'derivatives/exchanges/{id}',
                    json=resp_json,
                    status=200)

    response = cg.get_derivatives_exchange_info(id)
    assert response == resp_json

@responses.activate
def test_list_derivatives_exchanges():
    """Test /derivatives/exchanges/list."""
    resp_json = [{"id": "binance_futures", "name": "Binance (Futures)"}]
    responses.add(responses.GET,
                    END_POINTS + 'derivatives/exchanges/list',
                    json=resp_json,
                    status=200)

    response = cg.list_derivatives_exchanges()
    assert response == resp_json

#
# status_updates
#
@responses.activate
def test_get_status_updates():
    """Test /status_updates."""
    resp_json = {"status_updates": []}
    responses.add(responses.GET,
                    END_POINTS + 'status_updates',
                    json=resp_json,
                    status=200)

    response = cg.get_status_updates()
    assert response == resp_json

#
# events
#
@responses.activate
def test_list_events():
    """Test /events."""
    resp_json = {
        "data": [{
            "type": "Conference",
            "title": "GeckoCon - NFTs Gone Wild",
            "organizer": "CoinGecko"
        }],
        "count":
        1,
        "page":
        1
    }
    responses.add(responses.GET,
                    END_POINTS + 'events',
                    json=resp_json,
                    status=200)

    response = cg.list_events()
    assert response == resp_json

@responses.activate
def test_list_event_countries():
    """Test /events/countries."""
    resp_json = {
        "data": [{
            "country": "Taiwan",
            "code": "TW"
        }],
        "count": 66
    }
    responses.add(responses.GET,
                    END_POINTS + 'events/countries',
                    json=resp_json,
                    status=200)

    response = cg.list_event_countries()
    assert response == resp_json

@responses.activate
def test_list_event_types():
    """Test /events/types."""
    resp_json = {"data": ["Event", "Conference", "Meetup"], "count": 3}
    responses.add(responses.GET,
                    END_POINTS + 'events/types',
                    json=resp_json,
                    status=200)

    response = cg.list_event_types()
    assert response == resp_json

#
# global
#
@responses.activate
def test_get_global():
    """Test /global."""
    resp_json = {
        "data": {
            "active_cryptocurrencies": 9548,
            "upcoming_icos": 0,
            "ongoing_icos": 50,
            "ended_icos": 3375,
            "markets": 652,
            "total_market_cap": {
                "btc": 43713855.59427393,
            },
            "total_volume": {
                "btc": 3383889.526825504,
            },
            "market_cap_percentage": {
                "btc": 43.09051880180091
            },
            "market_cap_change_percentage_24h_usd": 5.889237875780905,
            "updated_at": 0
        }
    }
    responses.add(responses.GET,
                    END_POINTS + 'global',
                    json=resp_json,
                    status=200)

    response = cg.get_global()
    assert response == resp_json

@responses.activate
def test_get_global_defi():
    """Test /global/decentralized_finance_defi."""
    resp_json = {
        "data": {
            "defi_market_cap": "125093232243",
            "eth_market_cap": "422689571997",
            "defi_to_eth_ratio": "29",
            "trading_volume_24h": "13200319936",
            "defi_dominance": "5",
            "top_coin_name": "Terra",
            "top_coin_defi_dominance": 14
        }
    }
    responses.add(responses.GET,
                    END_POINTS + 'global/decentralized_finance_defi',
                    json=resp_json,
                    status=200)

    response = cg.get_global_defi()
    assert response == resp_json

#
# exchange_rates
#
@responses.activate
def test_get_exchange_rates():
    """Test /exchange_rates"""
    resp_json = {
        "rates": {
            "btc": {
                "name": "Bitcoin",
                "unit": "BTC",
                "value": 1,
                "type": "crypto"
            }
        }
    }
    responses.add(responses.GET,
                    END_POINTS + 'exchange_rates',
                    json=resp_json,
                    status=200)

    response = cg.get_exchange_rates()
    assert response == resp_json

#
# trending
#
@responses.activate
def test_get_search_trending():
    """Test /search/trending."""
    resp_json = {
        "coins": [{
            "item": {
                "id": "ethereum",
                "coin_id": 279,
                "name": "Ethereum",
                "symbol": "ETH",
                "market_cap_rank": 2,
                "slug": "ethereum",
                "price_btc": 0.06564781999611292,
                "score": 0
            }
        }],
        "exchanges": []
    }
    responses.add(responses.GET,
                    END_POINTS + 'search/trending',
                    json=resp_json,
                    status=200)

    response = cg.get_search_trending()
    assert response == resp_json

#
# companies
#
@responses.activate
def test_list_companies_holdings():
    """Test ​/companies​/public_treasury​/{coin_id}."""
    id = 'bitcoin'
    resp_json = {
        "total_holdings":
        208364.6658,
        "total_value_usd":
        11378517915.243517,
        "market_cap_dominance":
        1.11,
        "companies": [{
            "name": "MicroStrategy Inc.",
            "symbol": "NASDAQ:MSTR",
            "country": "US",
            "total_holdings": 114042,
            "total_entry_value_usd": 3160000000,
            "total_current_value_usd": 6227682294,
            "percentage_of_total_supply": 0.543
        }]
    }
    responses.add(responses.GET,
                    END_POINTS + f'companies/public_treasury/{id}',
                    json=resp_json,
                    status=200)

    response = cg.list_companies_holdings(id)
    assert response == resp_json
