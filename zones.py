from aurum_zones.data import fetch_ohlcv
from aurum_zones.zones import detect_zones
from aurum_zones.indicators import atr
from aurum_zones import config

df = fetch_ohlcv()
zones = detect_zones(df)
price = df["close"].iloc[-1]
a = atr(df, config.ATR_LENGTH).iloc[-1]

print(f"\nXAU/USD last bar: {df.index[-1]}  price={price:,.2f}  ATR={a:.2f}")
print(f"{'type':>7}  {'low':>10}  {'high':>10}  {'size':>6}  {'taps':>4}  "
      f"{'extreme':>7}  {'distance':>10}  {'created':>19}")
print("-" * 95)

for z in sorted(zones, key=lambda x: abs(price - (x["high"] + x["low"]) / 2)):
    dist = price - (z["high"] + z["low"]) / 2
    side = "above" if dist < 0 else "below"
    print(f"{z['type']:>7}  {z['low']:>10,.2f}  {z['high']:>10,.2f}  "
          f"{z['high'] - z['low']:>6,.2f}  {z['taps']:>4}  "
          f"{str(z.get('extreme', False)):>7}  "
          f"{abs(dist):>6,.2f} {side:<5}  {str(z['created'])[:19]}")

print(f"\nTotal zones: {len(zones)}")