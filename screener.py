import json
from urllib import request, parse

COINGECKO_MARKETS_URL = 'https://api.coingecko.com/api/v3/coins/markets'


def fetch_market_data(vs_currency='usd', per_page=10, page=1):
    """Fetch market data for cryptocurrencies from CoinGecko."""
    params = {
        'vs_currency': vs_currency,
        'order': 'market_cap_desc',
        'per_page': per_page,
        'page': page,
        'price_change_percentage': '24h'
    }
    url = COINGECKO_MARKETS_URL + '?' + parse.urlencode(params)
    with request.urlopen(url) as resp:
        data = json.loads(resp.read().decode())
    return data


def screen_by_price_change(data, pct_threshold=5.0):
    """Filter coins whose 24h change percentage is above pct_threshold."""
    screened = []
    for coin in data:
        change = coin.get('price_change_percentage_24h')
        if change is not None and change >= pct_threshold:
            screened.append(coin)
    return screened


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Simple crypto screener using CoinGecko API')
    parser.add_argument('--per-page', type=int, default=10, help='Number of coins to fetch')
    parser.add_argument('--threshold', type=float, default=5.0, help='24h percentage change threshold')
    args = parser.parse_args()

    data = fetch_market_data(per_page=args.per_page)
    screened = screen_by_price_change(data, pct_threshold=args.threshold)
    for coin in screened:
        name = coin.get('name')
        symbol = coin.get('symbol', '').upper()
        price = coin.get('current_price')
        change = coin.get('price_change_percentage_24h')
        print(f"{name} ({symbol}): {price} USD, 24h change {change}%")


if __name__ == '__main__':
    main()
