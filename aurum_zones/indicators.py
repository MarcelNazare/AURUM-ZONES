import pandas as pd


def atr(df, period=14):
    h, l, c = df["high"], df["low"], df["close"]
    tr = pd.concat(
        [h - l, (h - c.shift()).abs(), (l - c.shift()).abs()],
        axis=1,
    ).max(axis=1)
    return tr.rolling(period).mean()


def rsi(series, period=14):
    d = series.diff()
    g = d.clip(lower=0).ewm(alpha=1 / period, adjust=False).mean()
    l = (-d.clip(upper=0)).ewm(alpha=1 / period, adjust=False).mean()
    return 100 - 100 / (1 + g / l.replace(0, 1e-9))


def trend_direction(df, lookback=20):
    if len(df) < lookback:
        return "neutral"
    r = df.iloc[-lookback:]
    hh = r["high"].iloc[-1] > r["high"].iloc[0]
    hl = r["low"].iloc[-1]  > r["low"].iloc[0]
    lh = r["high"].iloc[-1] < r["high"].iloc[0]
    ll = r["low"].iloc[-1]  < r["low"].iloc[0]
    if hh and hl:
        return "uptrend"
    if lh and ll:
        return "downtrend"
    return "neutral"