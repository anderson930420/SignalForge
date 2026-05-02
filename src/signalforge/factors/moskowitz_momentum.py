"""Moskowitz Momentum Factor implementation."""


import pandas as pd


class MoskowitzMomentumFactor:
    """Moskowitz Momentum Factor.

    Based on Moskowitz, Ostdie, and Wells (2024):
    "Into the Darkness: An Empirical Investigation of Dark Matter Returns"

    Formula: signal_value = (CUMRET_12M - CUMRET_1M) / VOL_1M
    """

    name: str = "moskowitz_momentum"
    source: str = "moskowitz_2024"

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate Moskowitz Momentum Factor.

        Args:
            data: DataFrame with OHLCV columns (datetime, open, high, low, close, volume)

        Returns:
            DataFrame with 'signal_value' column
        """
        df = data.copy()

        if "close" not in df.columns:
            result = pd.DataFrame({"signal_value": [None]})
            return result

        lookback_12m = 252
        lookback_1m = 21
        vol_window = 21

        cumret_12m = df["close"].pct_change(lookback_12m)
        cumret_1m = df["close"].pct_change(lookback_1m)
        vol_1m = df["close"].pct_change().rolling(vol_window).std()

        numerator = cumret_12m - cumret_1m
        denominator = vol_1m

        signal_value = numerator / denominator
        signal_value = signal_value.where(denominator != 0, None)

        result = pd.DataFrame({"signal_value": signal_value})

        return result
