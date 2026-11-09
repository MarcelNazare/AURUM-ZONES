import requests, pandas as pd
from . import config


def fetch_ohlcv(symbol=config.SYMBOL, interval=config.INTERVAL,
                outputsize=config.OUTPUT_SIZE) -> pd.DataFrame:
    params = dict(symbol=symbol, interval=interval, outputsize=outputsize,
                  apikey=config.API_KEY, format="JSON", order="ASC")
    r = requests.get(config.BASE_URL, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()
    if data.get("status") == "error":
        raise RuntimeError(f"Twelve Data [{data.get('code')}]: {data.get('message')}")

    df = pd.DataFrame(data["values"])
    df["datetime"] = pd.to_datetime(df["datetime"])
    df.set_index("datetime", inplace=True)

    # Spot metals / forex do not include volume from Twelve Data.
    # Convert every numeric column that *does* exist, and fill volume with 0.
    if "volume" not in df.columns:
        df["volume"] = 0

    for c in ("open", "high", "low", "close", "volume"):
        df[c] = pd.to_numeric(df[c], errors="coerce")

    df.sort_index(inplace=True)
    return df