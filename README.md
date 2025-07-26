# crypto-screener

This repository contains a simple cryptocurrency screener implemented in Python.

## Usage

Run the screener to fetch the top cryptocurrencies by market cap and display those with a 24‑hour price change above a threshold:

```bash
python screener.py --per-page 10 --threshold 5
```

The script uses the public CoinGecko API. Network access is required for real data; the included tests mock API responses.
