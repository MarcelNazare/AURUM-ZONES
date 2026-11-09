from aurum_zones.data import fetch_ohlcv
from aurum_zones.zones import _pivots, _indecision, _imbalance
from aurum_zones.indicators import atr
from aurum_zones import config

df = fetch_ohlcv()
df["atr"] = atr(df, config.ATR_LENGTH)
ph, pl = _pivots(df)

for kind, pivots in (("supply", ph), ("demand", pl)):
    stage = dict(pivots=len(pivots), impulse=0, indecision=0, imbalance=0)
    for p in pivots:
        if p + config.SWING_LOOKBACK >= len(df):
            continue
        imp = df.iloc[p + 1:p + 1 + config.SWING_LOOKBACK]
        move = imp["high"].max() - imp["low"].min()
        if move < df["atr"].iloc[p] * config.IMPULSE_ATR_MULT:
            continue
        stage["impulse"] += 1
        z = _indecision(df, p)
        if not z:
            continue
        stage["indecision"] += 1
        zh, zl = z
        if zh == zl:
            continue
        if not _imbalance(df, zh, zl, p):
            continue
        stage["imbalance"] += 1
    print(kind, stage)