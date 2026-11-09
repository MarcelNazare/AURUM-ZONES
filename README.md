# Aurum Zones

<!-- NEW -->
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![Status: Beta](https://img.shields.io/badge/status-beta-orange.svg)]()

> A supply/demand strategy engine for **XAU/USD** that detects FVG-validated zones,
> scores directional bias from six confluence factors, and outputs ATR-stopped
> trade plans with exact entries, stops, and targets.

---

## What it does

Aurum Zones pulls live gold data from Twelve Data and applies a structured
supply/demand methodology to answer three questions on every run:

1. **Where are the meaningful zones?** — detected from the last indecision
   candle before an impulsive move, validated by a Fair Value Gap (FVG).
2. **Which direction is the market leaning?** — a transparent weighted bias
   built from trend, momentum, RSI, premium/discount, zone balance, and
   nearest structural level.
3. **What is the trade plan?** — entry, ATR-based stop loss, two take-profit
   targets, R:R, and position size — or an exact alert price to wait for.

The engine is deliberately conservative. It will say **`NO TRADE`** or
**`WAIT`** far more often than it fires a signal — because that is where the
edge lives.

---

## Features

| | |
|---|---|
| **Real market data** | Twelve Data API, XAU/USD from 1min to 1month |
| **FVG-based zones** | 3-bar Fair Value Gap detection tuned for continuous 24/5 gold |
| **Trend filter** | Longs only in uptrends, shorts only in downtrends |
| **First-tap rule** | Zones already tested are discarded — only the first retest counts |
| **Transparent bias** | Every confluence factor printed with its weighted contribution |
| **ATR risk model** | Stops placed ATR × 1.5 beyond the zone; size derived from 1% account risk |
| **Two targets** | TP1 at next opposing zone, TP2 at the one after |
| **Clear "wait" output** | When nothing is tradeable, prints the exact alert price and direction |

---

## Installation

### Requirements

- Python 3.9+
- A free [Twelve Data](https://twelvedata.com) account (API key)

### Steps

```powershell
# 1. Clone or create the project folder
cd "C:\path\to\aurum-zones"

# 2. Create a virtual environment (recommended)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure your API key
notepad .env
```

In `.env`, set:

```ini
AURUM_TWELVEDATA_KEY=your_real_twelve_data_key_here
```

### 5. Run

```powershell
python main.py
```

---

## Usage

### Standard run

```powershell
python main.py
```

Output:

```
==============================================================
  AURUM ZONES - XAU/USD
  Last bar: 2026-11-10 02:00:00  |  Price: 4,117.66
==============================================================

[BIAS] STRONG BULLISH   (score +4)
   ----------------------------------------------------------
   +2  HTF trend: uptrend (HH/HL)
   +1  5-bar momentum up
   +1  RSI 61.2 (>60, bullish)
   -1  Price in premium (favours shorts)
   +1  More demand zones (3 vs 1)
   +0  Nearest level: demand (48.21 away)

==============================================================
  TRADE PLANS
==============================================================

  No qualifying setups on the current bar.

--------------------------------------------------------------
[WATCH] Bias is STRONG BULLISH - waiting for a pullback.
   Current price:    4,117.66
   Wait for price:   4,069.45   (down 48.21)
   Type of zone:     demand
   >>> Set a price alert at 4,069.45 <<<
--------------------------------------------------------------
```

### When a setup is live

```
[LONG ] A  [PRICE_IN_ZONE]
   Zone:           4,062.10 - 4,068.80
   Entry:          4,065.45
   Stop loss:      4,055.00   (risk 10.45)
   Take profit 1:  4,090.00   (2.35R)
   Take profit 2:  4,148.20   (7.92R)
   Size:           0.96 oz  (0.01 lots)   Risk $100.00
```

---

## Project structure

<!-- UPDATED: added LICENSE and README.md -->
```
aurum-zones/
├── .env                        # API key (never commit)
├── .env.example                # template
├── .gitignore
├── LICENSE                     # MIT license
├── README.md                   # this file
├── requirements.txt
├── main.py                     # entry point
└── aurum_zones/
    ├── __init__.py
    ├── config.py               # constants, risk, parameters
    ├── data.py                 # Twelve Data fetch (FVG-safe)
    ├── indicators.py           # ATR, RSI, trend_direction
    ├── zones.py                # pivots, indecision candle, FVG imbalance
    ├── bias.py                 # weighted directional lean
    ├── signals.py              # trade plan generation
    └── report.py               # formatted console output
```

---

## Strategy

The engine implements the four rules from the original supply/demand
methodology:

### 1. Zone identification

A zone is the **last indecision candle** (small body, large wick) before an
impulsive move that exceeds `IMPULSE_ATR_MULT × ATR`. The zone boundaries are
the high and low of that candle.

### 2. Imbalance requirement

The zone must contain a **Fair Value Gap** — a three-bar pattern where:

- Bullish FVG: `bar3.low  > bar1.high`
- Bearish FVG: `bar3.high < bar1.low`

The gap must remain **unfilled** for `IMBALANCE_WINDOW` bars. This filters out
zones that formed on normal two-way price action rather than genuine
displacement.

### 3. Trend alignment

- **Longs** only from demand zones when the HTF is in an uptrend (higher highs + higher lows)
- **Shorts** only from supply zones when the HTF is in a downtrend (lower highs + lower lows)

Counter-trend setups are always skipped.

### 4. First-tap rule

Only the **first retest** of a zone is considered high probability. Zones with
`taps > 1` are discarded — they are more likely to break than hold.

### 5. Extreme zones

Zones furthest from price within the current leg get priority. These represent
the origin of the strongest institutional displacement.

---

## Directional bias

The bias engine scores six independent factors and sums them into a final
`score`:

| Factor | Weight | Meaning |
|---|---|---|
| HTF trend | ±2 | Higher highs/lows or lower highs/lows over 20 bars |
| 5-bar momentum | ±1 | Last close vs. 5 bars ago |
| RSI(14) | ±1 | > 60 bullish, < 40 bearish |
| Premium/Discount | ±1 | Price vs. midpoint of last 50 bars |
| Zone balance | ±1 | Demand count vs. supply count |
| Nearest level | 0 | Informational only |

| Total score | Label |
|---|---|
| ≥ +4 | STRONG BULLISH |
| +2 to +3 | BULLISH |
| -1 to +1 | NEUTRAL |
| -3 to -2 | BEARISH |
| ≤ -4 | STRONG BEARISH |

Bias is **not a prediction** — it is a transparent weighted lean that tells you
*which setups to look for*, not which will win.

---

## Configuration

All parameters live in `aurum_zones/config.py`. The ones worth tuning:

```python
SYMBOL         = "XAU/USD"      # instrument
INTERVAL       = "1h"           # 1min … 1month
OUTPUT_SIZE    = 250            # history bars fetched

IMPULSE_ATR_MULT = 1.2          # impulse strength threshold (× ATR)
SWING_LOOKBACK   = 5            # pivot confirmation window
IMBALANCE_WINDOW = 100          # bars an FVG must survive

ACCOUNT_BALANCE  = 10_000.0     # for position sizing
RISK_PER_TRADE   = 0.01         # 1% of account
ATR_SL_MULT      = 1.5          # stop distance (× ATR)
MIN_RR           = 1.5          # minimum reward:risk to emit a plan
```

### Tuning quick reference

| Symptom | Change |
|---|---|
| Zero zones detected | `IMPULSE_ATR_MULT = 1.0`, `IMBALANCE_WINDOW = 60` |
| Zones exist but all tapped | `OUTPUT_SIZE = 150` (fresher history) |
| Too many low-quality zones | `SWING_LOOKBACK = 8` (stricter pivots) |
| Trade plans all graded "B" | `MIN_RR = 2.0` (raise quality floor) |
| Signals outside key hours | Set `FILTER_SESSIONS = True` |

---

## Data source

Gold is fetched as **`XAU/USD`** from [Twelve Data](https://twelvedata.com).

**Note:** Twelve Data does **not** return volume for spot metals or forex.
The engine fills a `volume = 0` column so the DataFrame schema stays
consistent — none of the strategy logic uses volume.

**Rate limits (free tier):** 8 calls/minute, 800/day. A single `main.py` run
consumes 1 call. Running in a tight loop will trigger `429` responses —
add a `time.sleep()` or use a scheduler if you plan to run it frequently.

---

## Roadmap

Prioritised by impact on real trading outcomes:

- [ ] **Backtester** — walk history bar-by-bar, report win rate / average R per grade
- [ ] **Signal journal** — SQLite log of every emitted plan with eventual outcome
- [ ] **Session filter** — gate signals to London–NY overlap (13:00–17:00 UTC)
- [ ] **Rate-limit retry** — exponential backoff on `429` responses
- [ ] **Alerts** — Telegram / email on `[CALL]` signals
- [ ] **Zone merging** — combine overlapping same-side zones
- [ ] **Fixed tap counter** — count retests, not bars
- [ ] **Chart output** — matplotlib candles with zones and plans drawn

---

## Disclaimer

This software is provided for **educational purposes only**. It is not
financial advice, not a signal service, and not a guarantee of profit.

- Always test on a **demo account** before risking real capital
- Backtest thoroughly before trusting any signal
- Gold's daily range (30–60 USD) can wipe an account sized with FX
  assumptions — size positions with the ATR-based model, not fixed lots
- The author accepts no responsibility for trading losses

**Trade at your own risk.**

---

<!-- UPDATED: expanded license section -->
## License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE)
file for the full text.

**In short:**

- ✅ Commercial use
- ✅ Modification
- ✅ Distribution
- ✅ Private use
- ❌ No warranty
- ❌ No liability

You are free to use this code in any project, including commercial ones.
Just keep the copyright notice intact.

```
MIT License

Copyright (c) 2026 Marcel
```

---

<!-- NEW -->
## Contributing

Issues and pull requests are welcome. Before opening a PR:

1. Run `python main.py` and confirm the pipeline still works end-to-end
2. Keep changes focused — one feature or fix per PR
3. If you change strategy parameters, update the *Configuration* section of this README
4. If you change the bias logic, update the *Directional bias* table

This is a personal research project, so responses may be slow — but everything
reasonable gets read.

---

<!-- NEW -->
## Acknowledgements

- Strategy concept based on supply/demand and Fair Value Gap methodology
- Market data provided by [Twelve Data](https://twelvedata.com)
- Built with [pandas](https://pandas.pydata.org/) and [NumPy](https://numpy.org/)


---
