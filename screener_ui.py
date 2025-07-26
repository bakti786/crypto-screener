import streamlit as st
import requests
import pandas as pd

st.set_page_config(layout="wide")
st.title("🧠 DEX Crypto Screener – Supertrend Style")


@st.cache_data(show_spinner=False)
def get_coingecko_trending() -> pd.DataFrame:
    """Fetch trending coins from CoinGecko.

    Returns
    -------
    pandas.DataFrame
        DataFrame with coin name, symbol, price (BTC) and a CoinGecko URL.
    """
    url = "https://api.coingecko.com/api/v3/search/trending"
    columns = ["name", "symbol", "price", "url"]
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        data = res.json()
        coins = data.get("coins", [])
        rows = []
        for entry in coins:
            item = entry.get("item", {})
            coin_id = item.get("id")
            rows.append(
                {
                    "name": item.get("name"),
                    "symbol": item.get("symbol"),
                    "price": float(item.get("price_btc") or 0),
                    "url": f"https://www.coingecko.com/en/coins/{coin_id}" if coin_id else None,
                }
            )
        return pd.DataFrame(rows, columns=columns)
    except requests.exceptions.RequestException as exc:
        st.error(f"Gagal mengambil data dari CoinGecko: {exc}")
        return pd.DataFrame(columns=columns)
    except ValueError:
        st.error("Gagal memproses data JSON. Mungkin API sedang bermasalah.")
        return pd.DataFrame(columns=columns)


def compute_supertrend(df: pd.DataFrame, atr_period: int = 10, atr_mult: float = 1.5) -> pd.DataFrame:
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
    tr = pd.concat(
        [
            df["high"] - df["low"],
            (df["high"] - df["close"].shift()).abs(),
            (df["low"] - df["close"].shift()).abs(),
        ],
        axis=1,
    ).max(axis=1)
    if len(df) < atr_period:
        st.warning("Not enough data for ATR calculation")
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


def supertrend_signals(df: pd.DataFrame, atr_period: int = 10, atr_mult: float = 1.5) -> pd.DataFrame:
    """Return only rows where a new trend is detected."""
    df = compute_supertrend(df.copy(), atr_period=atr_period, atr_mult=atr_mult)
    return df[df["signal"] != 0]


if __name__ == "__main__":
    refresh = st.button("Refresh Data")
    if refresh:
        get_coingecko_trending.clear()
    data = get_coingecko_trending()

    signals = supertrend_signals(data)

    st.subheader("🔥 New Trend Signals Today")
    st.dataframe(signals[["name", "symbol", "price", "trend", "signal", "url"]])
