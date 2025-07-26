import streamlit as st
import requests
import pandas as pd

st.set_page_config(layout="wide")
st.title("🧠 DEX Crypto Screener – Supertrend Style")

@st.cache_data
def get_dex_data(limit=30):
    url = "https://api.dexscreener.com/latest/dex/pairs"
    res = requests.get(url)
    data = res.json()['pairs'][:limit]
    rows = []
    for d in data:
        rows.append({
            'pair': d['baseToken']['symbol'] + '/' + d['quoteToken']['symbol'],
            'price': float(d['priceUsd']) if d['priceUsd'] else 0,
            'volume': float(d['volume']['h24']) if d['volume']['h24'] else 0,
            'chain': d['chainId'],
            'dex': d['dexId'],
            'url': d['url']
        })
    return pd.DataFrame(rows)

def compute_supertrend(df, atr_period=10, atr_mult=1.5):
    df['high'] = df['price'] * 1.02
    df['low'] = df['price'] * 0.98
    df['close'] = df['price']

    hl2 = (df['high'] + df['low']) / 2
    tr = pd.concat([
        df['high'] - df['low'],
        (df['high'] - df['close'].shift()).abs(),
        (df['low'] - df['close'].shift()).abs(),
    ], axis=1).max(axis=1)
    atr = tr.rolling(atr_period, min_periods=atr_period).mean()

    df['upperBand'] = hl2 + atr_mult * atr
    df['lowerBand'] = hl2 - atr_mult * atr
    df['trend'] = 1
    for i in range(1, len(df)):
        if df['close'][i] > df['upperBand'][i-1]:
            df.loc[i, 'trend'] = 1
        elif df['close'][i] < df['lowerBand'][i-1]:
            df.loc[i, 'trend'] = -1
        else:
            df.loc[i, 'trend'] = df.loc[i-1, 'trend']
            if df.loc[i, 'trend'] == 1:
                df.loc[i, 'lowerBand'] = max(df['lowerBand'][i], df['lowerBand'][i-1])
            else:
                df.loc[i, 'upperBand'] = min(df['upperBand'][i], df['upperBand'][i-1])
    df['signal'] = df['trend'].diff()
    return df

if __name__ == "__main__":
    data = get_dex_data()
    data = compute_supertrend(data)
    signals = data[data['signal'] != 0]

    st.subheader("🔥 New Trend Signals Today")
    st.dataframe(signals[['pair', 'price', 'trend', 'signal', 'volume', 'url']])
