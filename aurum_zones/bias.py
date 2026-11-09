from .indicators import rsi, trend_direction


def directional_bias(df, zones):
    f, s = [], 0
    price = df["close"].iloc[-1]

    t = trend_direction(df)
    if t == "uptrend":
        s += 2
        f.append(("HTF trend: uptrend (HH/HL)", 2))
    elif t == "downtrend":
        s -= 2
        f.append(("HTF trend: downtrend (LL/LH)", -2))
    else:
        f.append(("HTF trend: neutral", 0))

    c = df["close"].iloc[-6:].values
    if c[-1] > c[0]:
        s += 1
        f.append(("5-bar momentum up", 1))
    else:
        s -= 1
        f.append(("5-bar momentum down", -1))

    r = rsi(df["close"]).iloc[-1]
    if r > 60:
        s += 1
        f.append((f"RSI {r:.1f} (>60, bullish)", 1))
    elif r < 40:
        s -= 1
        f.append((f"RSI {r:.1f} (<40, bearish)", -1))
    else:
        f.append((f"RSI {r:.1f} (neutral)", 0))

    rec = df.iloc[-50:]
    mid = (rec["high"].max() + rec["low"].min()) / 2
    if price < mid:
        s += 1
        f.append(("Price in discount (favours longs)", 1))
    else:
        s -= 1
        f.append(("Price in premium (favours shorts)", -1))

    bull = sum(1 for z in zones if z["type"] == "demand")
    bear = sum(1 for z in zones if z["type"] == "supply")
    if bull > bear:
        s += 1
        f.append((f"More demand zones ({bull} vs {bear})", 1))
    elif bear > bull:
        s -= 1
        f.append((f"More supply zones ({bear} vs {bull})", -1))
    else:
        f.append((f"Balanced zones ({bull} each)", 0))

    if zones:
        dh = [z["high"] for z in zones if z["type"] == "demand" and z["high"] < price]
        sl = [z["low"]  for z in zones if z["type"] == "supply" and z["low"]  > price]
        dd = price - max(dh) if dh else float("inf")
        sd = min(sl) - price if sl else float("inf")
        f.append((f"Nearest level: {'demand' if dd < sd else 'supply'} "
                  f"({min(dd, sd):.2f} away)", 0))

    if s >= 4:
        label = "STRONG_BULLISH"
    elif s >= 2:
        label = "BULLISH"
    elif s <= -4:
        label = "STRONG_BEARISH"
    elif s <= -2:
        label = "BEARISH"
    else:
        label = "NEUTRAL"

    return {"bias": label, "score": s, "factors": f}