from . import config
from .indicators import atr


def _size(bal, rp, dist):
    return (bal * rp) / dist if dist > 0 else 0


def generate_trade_plans(df, zones, bias,
                         balance=config.ACCOUNT_BALANCE,
                         risk=config.RISK_PER_TRADE):
    if df.empty or not zones:
        return []
    price = df["close"].iloc[-1]
    a = atr(df, config.ATR_LENGTH).iloc[-1]
    plans = []

    def add(direction, z):
        if z["taps"] > 1:
            return
        entry = (z["high"] + z["low"]) / 2

        if direction == "LONG":
            sl = z["low"] - a * config.ATR_SL_MULT
            rk = entry - sl
            if rk <= 0:
                return
            opp = sorted(
                [s for s in zones if s["type"] == "supply" and s["low"] > entry],
                key=lambda s: s["low"],
            )
            tp1 = opp[0]["low"] if opp else entry + rk * 2
            tp2 = opp[1]["low"] if len(opp) > 1 else entry + rk * 4
            rr1 = (tp1 - entry) / rk
            rr2 = (tp2 - entry) / rk
        else:
            sl = z["high"] + a * config.ATR_SL_MULT
            rk = sl - entry
            if rk <= 0:
                return
            opp = sorted(
                [d for d in zones if d["type"] == "demand" and d["high"] < entry],
                key=lambda d: d["high"],
                reverse=True,
            )
            tp1 = opp[0]["high"] if opp else entry - rk * 2
            tp2 = opp[1]["high"] if len(opp) > 1 else entry - rk * 4
            rr1 = (entry - tp1) / rk
            rr2 = (entry - tp2) / rk

        if z["low"] <= price <= z["high"]:
            status = "PRICE_IN_ZONE"
        elif (direction == "LONG"  and price > z["high"]) or \
             (direction == "SHORT" and price < z["low"]):
            status = "PENDING_RETEST"
        else:
            status = "BROKEN"

        q = "A+" if rr1 >= 3 else "A" if rr1 >= 2 else "B" if rr1 >= config.MIN_RR else None
        if not q:
            return

        plans.append(dict(
            direction=direction, status=status, quality=q,
            entry=entry, entry_zone=(z["low"], z["high"]),
            sl=sl, tp1=tp1, tp2=tp2, rr1=rr1, rr2=rr2,
            risk_distance=rk, risk_usd=balance * risk,
            position_size=_size(balance, risk, rk),
        ))

    if bias["score"] >= 2:
        for z in zones:
            if z["type"] == "demand":
                add("LONG", z)

    if bias["score"] <= -2:
        for z in zones:
            if z["type"] == "supply":
                add("SHORT", z)

    o = {"PRICE_IN_ZONE": 0, "PENDING_RETEST": 1, "BROKEN": 2}
    qo = {"A+": 0, "A": 1, "B": 2}
    plans.sort(key=lambda p: (o[p["status"]], qo[p["quality"]]))
    return plans