"""
Aurum Zones - entry point
Run with:  python main.py
"""

import sys
from pathlib import Path

# Ensure the folder containing main.py is on sys.path (fixes some IDE runners)
sys.path.insert(0, str(Path(__file__).resolve().parent))

from aurum_zones.data import fetch_ohlcv
from aurum_zones.zones import detect_zones
from aurum_zones.bias import directional_bias
from aurum_zones.signals import generate_trade_plans
from aurum_zones.report import print_report, print_direction_call


def main():
    print("Fetching XAU/USD ...")
    df = fetch_ohlcv()
    zones = detect_zones(df)
    bias = directional_bias(df, zones)
    plans = generate_trade_plans(df, zones, bias)
    print_report(df, bias, plans)
    print_direction_call(bias, plans, df)


if __name__ == "__main__":
    main()