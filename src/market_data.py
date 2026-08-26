import requests
from datetime import datetime, timezone


API_URL = "https://api.exchange.coinbase.com/products/BTC-USD/candles"


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

    # Coinbase returns:
    # [time, low, high, open, close, volume]

    candles = sorted(candles, key=lambda x: x[0])

    data = []

    for candle in candles[-limit:]:
        data.append({
            "time": datetime.fromtimestamp(
                candle[0],
                tz=timezone.utc
            ).isoformat(),

            "open": float(candle[3]),
            "high": float(candle[2]),
            "low": float(candle[1]),
            "close": float(candle[4]),
            "volume": float(candle[5])
        })

    return data


if __name__ == "__main__":

    btc = get_btc_data()

    print("BTC Predictor")
    print("=" * 40)

    print(f"Number of candles: {len(btc)}")

    if btc:
        latest = btc[-1]

        print(f"Latest price: ${latest['close']:,.2f}")
        print(f"Latest candle: {latest['time']}")
        print(f"Volume: {latest['volume']:,.4f}")
