import os, sys
from datetime import time as dt_time
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("AURUM_TWELVEDATA_KEY")
if not API_KEY:
    sys.exit("ERROR: AURUM_TWELVEDATA_KEY missing. Add to .env")

SYMBOL         = "XAU/USD"
INTERVAL       = "1h"
OUTPUT_SIZE    = 250        # was 500 - fresher history, more intact gaps
BASE_URL       = "https://api.twelvedata.com/time_series"

SWING_LOOKBACK   = 5
IMPULSE_ATR_MULT = 1.2      # was 1.8 - gold 1h needs smaller threshold
BASE_LOOKBACK    = 3
ATR_LENGTH       = 14
MITIGATION_TYPE  = "Wick"
IMBALANCE_WINDOW = 100      # NEW - only scan gaps within N bars of zone creation

ACCOUNT_BALANCE = 10_000.0
RISK_PER_TRADE  = 0.01
ATR_SL_MULT     = 1.5
MIN_RR          = 1.5

SESSION_START   = dt_time(13, 0)
SESSION_END     = dt_time(17, 0)
FILTER_SESSIONS = True

