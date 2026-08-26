import csv
import os
import time
import requests

from datetime import datetime, timezone, timedelta


API_URL = "https://api.exchange.coinbase.com/products/BTC-USD/candles"
DATA_FILE = "data/btc_1h.csv"

GRANULARITY = 3600
MAX_CANDLES = 300

# Approximately 2 years
DAYS = 730


def fetch_candles(start, end):
    params = {
        "granularity": GRANULARITY,
        "start": start.isoformat(),
        "end": end.isoformat()
    }

    response = requests.get(
        API_URL,
        params=params,
        timeout=20,
        headers={
            "User-Agent": "BTC-Predictor/0.1"
        }
    )

    response.raise_for_status()

    return response.json()


def load_existing():
    existing = {}

    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", newline="") as file:
            reader = csv.DictReader(file)

            for row in reader:
                existing[row["timestamp"]] = row

    return existing


def save_data(data):

    os.makedirs("data", exist_ok=True)

    with open(DATA_FILE, "w", newline="") as file:

        fields = [
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
            fieldnames=fields
        )

        writer.writeheader()

        for row in sorted(
            data.values(),
            key=lambda x: int(x["timestamp"])
        ):
            writer.writerow(row)


def main():

    existing = load_existing()

    end = datetime.now(timezone.utc)

    start = end - timedelta(days=DAYS)

    chunk = timedelta(
        seconds=GRANULARITY * MAX_CANDLES
    )

    total_requests = 0

    print("BTC Historical Data Downloader")
    print("=" * 50)

    while start < end:

        chunk_end = min(
            start + chunk,
            end
        )

        print(
            f"Downloading: "
            f"{start.isoformat()} → "
            f"{chunk_end.isoformat()}"
        )

        candles = fetch_candles(
            start,
            chunk_end
        )

        for candle in candles:

            timestamp = int(candle[0])

            row = {
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
            }

            existing[str(timestamp)] = row

        total_requests += 1

        print(
            f"Received: {len(candles)} candles"
        )

        start = chunk_end

        # Be polite to the API
        time.sleep(0.3)

    save_data(existing)

    print()
    print("=" * 50)
    print(f"Requests: {total_requests}")
    print(f"Total candles: {len(existing)}")
    print(f"Saved to: {DATA_FILE}")


if __name__ == "__main__":
    main()
