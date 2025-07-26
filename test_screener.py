import json
from unittest.mock import patch, MagicMock

import screener

sample_data = [
    {
        'id': 'bitcoin',
        'symbol': 'btc',
        'name': 'Bitcoin',
        'current_price': 30000,
        'price_change_percentage_24h': 10.0,
    },
    {
        'id': 'ethereum',
        'symbol': 'eth',
        'name': 'Ethereum',
        'current_price': 2000,
        'price_change_percentage_24h': 3.0,
    },
]

# Mock data for the /search/trending endpoint
trending_json = {
    "coins": [
        {
            "item": {
                "id": "bitcoin",
                "name": "Bitcoin",
                "symbol": "BTC",
                "price_btc": 1.0,
            }
        },
        {
            "item": {
                "id": "ethereum",
                "name": "Ethereum",
                "symbol": "ETH",
                "price_btc": 0.065,
            }
        },
    ]
}


@patch('urllib.request.urlopen')
def test_fetch_market_data(mock_urlopen):
    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps(sample_data).encode()
    mock_urlopen.return_value.__enter__.return_value = mock_response

    data = screener.fetch_market_data(per_page=2)
    assert data == sample_data
    assert mock_urlopen.called


def test_screen_by_price_change():
    filtered = screener.screen_by_price_change(sample_data, pct_threshold=5)
    assert filtered == [sample_data[0]]


@patch('screener_ui.requests.get')
def test_get_coingecko_trending(mock_get):
    import screener_ui

    mock_response = MagicMock()
    mock_response.json.return_value = trending_json
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    df = screener_ui.get_coingecko_trending()
    assert {"name", "symbol", "price"}.issubset(df.columns)
    assert len(df) == len(trending_json["coins"])
    assert mock_get.called
