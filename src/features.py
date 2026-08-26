import pandas as pd
import numpy as np


INPUT_FILE = "data/btc_1h.csv"
OUTPUT_FILE = "data/btc_features.csv"


def calculate_features(df):

    df = df.copy()

    # -------------------------
    # Returns
    # -------------------------

    df["return_1h"] = df["close"].pct_change(1)
    df["return_4h"] = df["close"].pct_change(4)
    df["return_12h"] = df["close"].pct_change(12)
    df["return_24h"] = df["close"].pct_change(24)

    # -------------------------
    # Moving averages
    # -------------------------

    df["ema_9"] = df["close"].ewm(
        span=9,
        adjust=False
    ).mean()

    df["ema_20"] = df["close"].ewm(
        span=20,
        adjust=False
    ).mean()

    df["ema_50"] = df["close"].ewm(
        span=50,
        adjust=False
    ).mean()

    df["ema_200"] = df["close"].ewm(
        span=200,
        adjust=False
    ).mean()

    # -------------------------
    # RSI
    # -------------------------

    delta = df["close"].diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()

    rs = avg_gain / avg_loss

    df["rsi_14"] = 100 - (
        100 / (1 + rs)
    )

    # -------------------------
    # MACD
    # -------------------------

    ema_12 = df["close"].ewm(
        span=12,
        adjust=False
    ).mean()

    ema_26 = df["close"].ewm(
        span=26,
        adjust=False
    ).mean()

    df["macd"] = ema_12 - ema_26

    df["macd_signal"] = df["macd"].ewm(
        span=9,
        adjust=False
    ).mean()

    df["macd_hist"] = (
        df["macd"] -
        df["macd_signal"]
    )

    # -------------------------
    # Bollinger Bands
    # -------------------------

    middle = df["close"].rolling(20).mean()
    std = df["close"].rolling(20).std()

    df["bb_middle"] = middle
    df["bb_upper"] = middle + 2 * std
    df["bb_lower"] = middle - 2 * std

    df["bb_width"] = (
        (df["bb_upper"] - df["bb_lower"])
        / df["bb_middle"]
    )

    # -------------------------
    # Volatility
    # -------------------------

    df["volatility_24h"] = (
        df["return_1h"]
        .rolling(24)
        .std()
    )

    # -------------------------
    # Volume
    # -------------------------

    df["volume_ma_24h"] = (
        df["volume"]
        .rolling(24)
        .mean()
    )

    df["relative_volume"] = (
        df["volume"]
        / df["volume_ma_24h"]
    )

    # -------------------------
    # Candle structure
    # -------------------------

    df["candle_range"] = (
        df["high"] - df["low"]
    ) / df["close"]

    df["body_size"] = (
        abs(df["close"] - df["open"])
        / df["close"]
    )

    df["upper_wick"] = (
        df["high"]
        - df[["open", "close"]].max(axis=1)
    ) / df["close"]

    df["lower_wick"] = (
        df[["open", "close"]].min(axis=1)
        - df["low"]
    ) / df["close"]

    # -------------------------
    # EMA relationships
    # -------------------------

    df["price_vs_ema20"] = (
        df["close"] / df["ema_20"] - 1
    )

    df["price_vs_ema50"] = (
        df["close"] / df["ema_50"] - 1
    )

    df["ema20_vs_ema50"] = (
        df["ema_20"] / df["ema_50"] - 1
    )

    # -------------------------
    # Target
    # -------------------------

    future_price = df["close"].shift(-24)

    future_return = (
        future_price / df["close"] - 1
    )

    df["future_return_24h"] = future_return

    df["target"] = np.select(
        [
            future_return >= 0.02,
            future_return <= -0.02
        ],
        [
            1,
            -1
        ],
        default=0
    )

    return df


def main():

    print("Loading BTC dataset...")

    df = pd.read_csv(INPUT_FILE)

    print(f"Rows loaded: {len(df)}")

    df = calculate_features(df)

    # Remove rows where indicators
    # cannot yet be calculated.
    df = df.dropna()

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print()
    print("Feature Engineering Complete")
    print("=" * 50)

    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")

    print()
    print("Target distribution:")

    print(
        df["target"]
        .value_counts()
        .sort_index()
    )

    print()
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
