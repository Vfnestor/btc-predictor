import csv
import os
import requests
from datetime import datetime, timezone


API_URL = "https://api.exchange.coinbase.com/products/BTC-USD/candles"
DATA_FILE = "data/btc_1h.csv"


def get_btc_data(granularity=3600, limit=100):
    params = {
        "granularity": granularity
    }

    response = requests.get(
        API_URL,
        params=params,
        timeout=15,
        headers={
            "User-Agent": "BTC-Predictor/0.1"
        }
    )

    response.raise_for_status()

    candles = response.json()
    candles = sorted(candles, key=lambda x: x[0])

    data = []

    # Current hour is not complete, so don't use it.
    current_hour = int(
        datetime.now(timezone.utc).timestamp() // granularity
    ) * granularity

    for candle in candles:
        timestamp = int(candle[0])

        if timestamp >= current_hour:
            continue

        data.append({
            "time": datetime.fromtimestamp(
                timestamp,
                tz=timezone.utc
            ).isoformat(),

            "timestamp": timestamp,
            "open": float(candle[3]),
            "high": float(candle[2]),
            "low": float(candle[1]),
            "close": float(candle[4]),
            "volume": float(candle[5])
        })

    return data[-limit:]


def save_data(new_data):
    os.makedirs("data", exist_ok=True)

    existing = {}

    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", newline="") as file:
            reader = csv.DictReader(file)

            for row in reader:
                existing[row["timestamp"]] = row

    for row in new_data:
        existing[str(row["timestamp"])] = row

    combined = list(existing.values())

    combined.sort(key=lambda x: int(x["timestamp"]))

    with open(DATA_FILE, "w", newline="") as file:

        fieldnames = [
            "time",
            "timestamp",
            "open",
            "high",
            "low",
            "close",
            "volume"
        ]

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(combined)

    return len(combined)


if __name__ == "__main__":

    btc = get_btc_data()

    total = save_data(btc)

    print("BTC Predictor")
    print("=" * 40)

    print(f"New candles received: {len(btc)}")
    print(f"Total candles stored: {total}")

    if btc:
        latest = btc[-1]

        print(f"Latest closed price: ${latest['close']:,.2f}")
        print(f"Latest candle: {latest['time']}")
        print(f"Volume: {latest['volume']:,.4f}")

    print(f"Data file: {DATA_FILE}")
