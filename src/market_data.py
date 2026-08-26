import requests
from datetime import datetime, timezone


API_URL = "https://api.binance.com/api/v3/klines"


def get_btc_data(interval="1h", limit=100):
    params = {
        "symbol": "BTCUSDT",
        "interval": interval,
        "limit": limit
    }

    response = requests.get(API_URL, params=params, timeout=10)
    response.raise_for_status()

    candles = response.json()

    data = []

    for candle in candles:
        data.append({
            "time": datetime.fromtimestamp(
                candle[0] / 1000,
                tz=timezone.utc
            ).isoformat(),
            "open": float(candle[1]),
            "high": float(candle[2]),
            "low": float(candle[3]),
            "close": float(candle[4]),
            "volume": float(candle[5])
        })

    return data


if __name__ == "__main__":
    btc = get_btc_data()

    print("BTC Predictor")
    print("=" * 40)

    print(f"Number of candles: {len(btc)}")
    print(f"Latest price: ${btc[-1]['close']:,.2f}")
    print(f"Latest candle: {btc[-1]['time']}")
