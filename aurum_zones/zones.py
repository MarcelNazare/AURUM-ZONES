import pandas as pd
from . import config
from .indicators import atr


def _pivots(df, n=config.SWING_LOOKBACK):
    h, l = df["high"].values, df["low"].values
    ph, pl = [], []
    for i in range(n, len(df) - n):
        if h[i] == max(h[i - n:i + n + 1]):
            ph.append(i)
        if l[i] == min(l[i - n:i + n + 1]):
            pl.append(i)
    return ph, pl


def _indecision(df, p, n=config.BASE_LOOKBACK):
    base = df.iloc[max(0, p - n):p + 1]
    if base.empty:
        return None
    body = (base["close"] - base["open"]).abs()
    rng  = (base["high"] - base["low"]).replace(0, 1e-9)
    small = body <= rng * 0.35
    if not small.any():
        return None
    c = base.loc[base[small].index[-1]]
    return float(c["high"]), float(c["low"])


def _imbalance(df, zh, zl, start,
               mit=config.MITIGATION_TYPE,
               window=config.IMBALANCE_WINDOW,
               impulse_len=None):
    """
    Fair Value Gap (FVG) detection for continuous markets (XAU/USD, forex).
    
    A 2-bar gap doesn't exist on 24/5 instruments. Use the 3-bar FVG pattern:
      Bullish FVG: bar3.low  > bar1.high   -> gap between bar1.high and bar3.low
      Bearish FVG: bar3.high < bar1.low    -> gap between bar3.high and bar1.low

    A zone is valid if its impulse contains at least one unfilled FVG.
    """
    if impulse_len is None:
        impulse_len = config.SWING_LOOKBACK

    # FVG bars must fall within the impulse window (p ... p+impulse_len)
    scan_end = min(len(df) - 2, start + impulse_len + 1)

    for i in range(start, scan_end):
        bar1 = df.iloc[i]
        bar3 = df.iloc[i + 2]

        if bar3["low"] > bar1["high"]:              # bullish FVG
            g_lo, g_hi = float(bar1["high"]), float(bar3["low"])
            bullish = True
        elif bar3["high"] < bar1["low"]:            # bearish FVG
            g_lo, g_hi = float(bar3["high"]), float(bar1["low"])
            bullish = False
        else:
            continue

        # Look for a fill AFTER the FVG completes
        after = df.iloc[i + 3:min(len(df), i + 3 + window)]
        if after.empty:
            return True                             # FVG at end of history

        if mit == "Wick":
            fill_hit = (after["low"] <= g_lo) if bullish else (after["high"] >= g_hi)
        else:
            fill_hit = (after["close"] <= g_lo) if bullish else (after["close"] >= g_hi)

        if not fill_hit.any():
            return True                             # survived the window

    return False


def _taps(df, zh, zl, start):
    return sum(
        1 for i in range(start + 1, len(df))
        if df.iloc[i]["low"] <= zh and df.iloc[i]["high"] >= zl
    )


def detect_zones(df):
    df = df.copy()
    df["atr"] = atr(df, config.ATR_LENGTH)
    ph, pl = _pivots(df)
    out = []
    for kind, piv in (("supply", ph), ("demand", pl)):
        for p in piv:
            if p + config.SWING_LOOKBACK >= len(df):
                continue
            imp = df.iloc[p + 1:p + 1 + config.SWING_LOOKBACK]
            if imp.empty:
                continue
            if (imp["high"].max() - imp["low"].min()) < df["atr"].iloc[p] * config.IMPULSE_ATR_MULT:
                continue
            z = _indecision(df, p)
            if not z:
                continue
            zh, zl = z
            if zh == zl:
                continue
            if not _imbalance(df, zh, zl, p):
                continue
            out.append(dict(
                type=kind, high=zh, low=zl, start_idx=p,
                taps=_taps(df, zh, zl, p), created=df.index[p],
            ))
    price = df["close"].iloc[-1]
    if out:
        d = [abs(price - (z["high"] + z["low"]) / 2) for z in out]
        m = max(d)
        for z, x in zip(out, d):
            z["extreme"] = (x == m)
    return out