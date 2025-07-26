import streamlit as st
import requests
import pandas as pd

st.set_page_config(layout="wide")
st.title("\U0001F9E0 DEX Crypto Screener – Supertrend Style")

@st.cache_data
def get_dex_data(limit=30):
    url = "https://api.dexscreener.com/latest/dex/pairs"
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        data = res.json()
        if 'pairs' not in data:
            st.error("Data tidak tersedia dari DexScreener. Coba lagi nanti.")
            return pd.DataFrame()
        raw_pairs = data['pairs'][:limit]
        rows = []
        for d in raw_pairs:
            rows.append({
                'pair': d['baseToken']['symbol'] + '/' + d['quoteToken']['symbol'],
                'price': float(d['priceUsd']) if d['priceUsd'] else 0,
                'volume': float(d['volume']['h24']) if d['volume']['h24'] else 0,
                'chain': d['chainId'],
                'dex': d['dexId'],
                'url': d['url']
            })
        return pd.DataFrame(rows)
    except requests.exceptions.RequestException as e:
        st.error(f"Gagal mengambil data dari DEX Screener: {e}")
        return pd.DataFrame()
    except ValueError:
        st.error("Gagal memproses data JSON. Mungkin API sedang bermasalah.")
        return pd.DataFrame()

def compute_supertrend(df, atr_period=10, atr_mult=1.5):
    df['high'] = df['price'] * 1.02
    df['low'] = df['price'] * 0.98
    df['close'] = df['price']
    df['hlc3'] = (df['high'] + df['low'] + df['close']) / 3
    df['atr'] = df['high'].rolling(atr_period).max() - df['low'].rolling(atr_period).min()
    df['upperBand'] = df['hlc3'] + atr_mult * df['atr']
    df['lowerBand'] = df['hlc3'] - atr_mult * df['atr']
    df['trend'] = 1
    for i in range(1, len(df)):
        if df['close'][i-1] > df['lowerBand'][i-1]:
            df.loc[i, 'trend'] = 1
        elif df['close'][i-1] < df['upperBand'][i-1]:
            df.loc[i, 'trend'] = -1
        else:
            df.loc[i, 'trend'] = df.loc[i-1, 'trend']
    df['signal'] = df['trend'].diff()
    return df

data = get_dex_data()
data = compute_supertrend(data)
signals = data[data['signal'] != 0]

st.subheader("\U0001F525 Sinyal Trend Baru Hari Ini")

# === FILTER UI ===
selected_trend = st.selectbox("Filter Sinyal:", options=["Semua", "Long Only", "Short Only"])
min_volume = st.slider("Minimum Volume (USD)", min_value=0, max_value=5000000, value=10000, step=1000)

# === FILTER LOGIC ===
if selected_trend == "Long Only":
    signals = signals[signals['trend'] == 1]
elif selected_trend == "Short Only":
    signals = signals[signals['trend'] == -1]

signals = signals[signals['volume'] >= min_volume]

st.dataframe(signals[['pair', 'price', 'trend', 'signal', 'volume', 'url']])
