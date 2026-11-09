"""
Aurum Zones - formatted console report.
"""

DIR = {
    "STRONG_BULLISH": "STRONG BULLISH",
    "BULLISH":        "BULLISH",
    "NEUTRAL":        "NEUTRAL",
    "BEARISH":        "BEARISH",
    "STRONG_BEARISH": "STRONG BEARISH",
}


def print_report(df, bias, plans):
    """Print the main header, bias breakdown, and any trade plans."""
    price = df["close"].iloc[-1]
    ts = df.index[-1]
    line = "=" * 62

    print(f"\n{line}")
    print(f"  AURUM ZONES - XAU/USD")
    print(f"  Last bar: {ts}  |  Price: {price:,.2f}")
    print(line)

    print(f"\n[BIAS] {DIR[bias['bias']]}   (score {bias['score']:+d})")
    print("   " + "-" * 58)
    for txt, pts in bias["factors"]:
        print(f"   {pts:+d}  {txt}")
    print("\n   (Bias is a weighted lean, not a prediction.)")

    print(f"\n{line}\n  TRADE PLANS\n{line}")
    if not plans:
        print("\n  No qualifying setups on the current bar.\n")
        return

    for p in plans:
        side = "LONG " if p["direction"] == "LONG" else "SHORT"
        zl, zh = p["entry_zone"]
        print(f"\n[{side}] {p['quality']}  [{p['status']}]")
        print(f"   Zone:           {zl:,.2f} - {zh:,.2f}")
        print(f"   Entry:          {p['entry']:,.2f}")
        print(f"   Stop loss:      {p['sl']:,.2f}   (risk {p['risk_distance']:,.2f})")
        print(f"   Take profit 1:  {p['tp1']:,.2f}   ({p['rr1']:.2f}R)")
        print(f"   Take profit 2:  {p['tp2']:,.2f}   ({p['rr2']:.2f}R)")
        print(f"   Size:           {p['position_size']:.2f} oz  "
              f"({p['position_size'] / 100:.2f} lots)   "
              f"Risk ${p['risk_usd']:.2f}")


def print_direction_call(bias, plans, df=None):
    """
    Print the final actionable line.

    If a plan exists -> gives entry / stop / target.
    If bias is aligned but no zone is at price -> gives the EXACT alert price.
    """
    longs  = [p for p in plans if p["direction"] == "LONG"]
    shorts = [p for p in plans if p["direction"] == "SHORT"]

    print("\n" + "-" * 62)

    # --- 1. A plan exists ---------------------------------------------------
    if bias["score"] >= 2 and longs:
        p = longs[0]
        print(f"[CALL] LONG from demand.")
        print(f"   Entry:        {p['entry']:,.2f}")
        print(f"   Stop loss:    {p['sl']:,.2f}")
        print(f"   Take profit:  {p['tp1']:,.2f}   ({p['rr1']:.2f}R)")

    elif bias["score"] <= -2 and shorts:
        p = shorts[0]
        print(f"[CALL] SHORT from supply.")
        print(f"   Entry:        {p['entry']:,.2f}")
        print(f"   Stop loss:    {p['sl']:,.2f}")
        print(f"   Take profit:  {p['tp1']:,.2f}   ({p['rr1']:.2f}R)")

    # --- 2. Bias aligned, but nothing to trade yet -------------------------
    elif abs(bias["score"]) >= 2 and df is not None:
        current = df["close"].iloc[-1]
        direction_word = "down" if bias["score"] > 0 else "up"
        target_type = "demand" if bias["score"] > 0 else "supply"

        # Pull the nearest-zone distance computed in bias.py
        dist = None
        for txt, _ in bias["factors"]:
            if txt.startswith("Nearest level:"):
                # "Nearest level: demand (48.21 away)"
                try:
                    dist = float(txt.split("(")[1].split(" away")[0])
                except (IndexError, ValueError):
                    pass
                break

        print(f"[WATCH] Bias is {DIR[bias['bias']]} - waiting for a pullback.")

        if dist is not None:
            alert_price = current - dist if bias["score"] > 0 else current + dist
            print(f"   Current price:    {current:,.2f}")
            print(f"   Wait for price:   {alert_price:,.2f}   "
                  f"({direction_word} {dist:,.2f})")
            print(f"   Type of zone:     {target_type}")
            print(f"   >>> Set a price alert at {alert_price:,.2f} <<<")
        else:
            print(f"   Wait for a {target_type} tap that aligns with the trend.")

    # --- 3. Nothing aligned -------------------------------------------------
    else:
        print(f"[CALL] NO TRADE - bias is {DIR[bias['bias']]} "
              f"(not strong enough to trade).")

    print("-" * 62)