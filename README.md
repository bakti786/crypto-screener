# crypto-screener

This repository contains a simple cryptocurrency screener implemented in Python.

## Usage

Run the screener to fetch the top cryptocurrencies by market cap and display those with a 24‑hour price change above a threshold (default `2.0`):

```bash
python screener.py --per-page 10 --threshold 2
```

The script uses the public CoinGecko API. Network access is required for real data; the included tests mock API responses.

## Installation

Install the Python dependencies with:

```bash
pip install -r requirements.txt
```

## Streamlit UI

The repository also includes a simple Streamlit UI that fetches trending data from CoinGecko rather than DexScreener and highlights new trend signals. Run it with:

```bash
streamlit run screener_ui.py
```
Trending coins are retrieved from the [CoinGecko trending endpoint](https://api.coingecko.com/api/v3/search/trending). You can visit that URL to see the raw JSON response.
