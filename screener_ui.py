import streamlit as st
import requests
import pandas as pd

st.set_page_config(layout="wide")
st.title("🧠 DEX Crypto Screener – Supertrend Style")

@st.cache_data
def get_dex_data(limit=30):
    """Fetch recent pair data from Dexscreener.

    Parameters
    ----------
    limit : int
        Number of rows to return.

    Returns
    -------
    pandas.DataFrame
        DataFrame with pair information such as symbol, price and volume.
    """

    url = "https://api.dexscreener.com/latest/dex/pairs"
    try:
        res = requests.get(url)
        res.raise_for_status()
    except requests.RequestException as exc:
        st.error(f"Failed to fetch data: {exc}")
        return pd.DataFrame(columns=["pair", "price", "volume", "chain", "dex", "url"])

    data = res.json().get("pairs", [])[:limit]
    rows = []
    for d in data:
        rows.append({
            "pair": d["baseToken"]["symbol"] + "/" + d["quoteToken"]["symbol"],
            "price": float(d.get("priceUsd") or 0),
            "volume": float(d.get("volume", {}).get("h24") or 0),
            "chain": d.get("chainId"),
            "dex": d.get("dexId"),
            "url": d.get("url"),
        })
    return pd.DataFrame(rows)

def compute_supertrend(df, atr_period=10, atr_mult=1.5):
    """Calculate the Supertrend indicator.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing at least a ``price`` column.
    atr_period : int, optional
        Period used for ATR calculation, by default 10.
    atr_mult : float, optional
        Multiplier applied to the ATR, by default 1.5.

    Returns
    -------
    pandas.DataFrame
        The input DataFrame with additional Supertrend columns.
    """

    df["high"] = df["price"] * 1.02
    df["low"] = df["price"] * 0.98
    df["close"] = df["price"]

    hl2 = (df["high"] + df["low"]) / 2
    tr = pd.concat([
        df["high"] - df["low"],
        (df["high"] - df["close"].shift()).abs(),
        (df["low"] - df["close"].shift()).abs(),
    ], axis=1).max(axis=1)
    atr = tr.rolling(atr_period, min_periods=atr_period).mean()

    df["upper_band"] = hl2 + atr_mult * atr
    df["lower_band"] = hl2 - atr_mult * atr
    df["trend"] = 1
    for i in range(1, len(df)):
        if df["close"][i] > df["upper_band"][i - 1]:
            df.loc[i, "trend"] = 1
        elif df["close"][i] < df["lower_band"][i - 1]:
            df.loc[i, "trend"] = -1
        else:
            df.loc[i, "trend"] = df.loc[i - 1, "trend"]
            if df.loc[i, "trend"] == 1:
                df.loc[i, "lower_band"] = max(df["lower_band"][i], df["lower_band"][i - 1])
            else:
                df.loc[i, "upper_band"] = min(df["upper_band"][i], df["upper_band"][i - 1])
    df["signal"] = df["trend"].diff()
    return df

if __name__ == "__main__":
    data = get_dex_data()
    data = compute_supertrend(data)
    signals = data[data['signal'] != 0]

    st.subheader("🔥 New Trend Signals Today")
    st.dataframe(signals[['pair', 'price', 'trend', 'signal', 'volume', 'url']])
