"""Moskowitz Momentum Factor implementation.

Based on Moskowitz, Ostdie, and Wells (2024):
"Into the Darkness: An Empirical Investigation of Dark Matter Returns"

Formula: signal_value[t] = close[t - skip_days] / close[t - lookback_days] - 1

Parameters:
- lookback_days = 252 (12 months of trading days)
- skip_days = 21 (1 month of trading days)
"""


import pandas as pd


class MoskowitzMomentumFactor:
    """Moskowitz Momentum Factor implementation."""

    name: str = "moskowitz_momentum"
    source: str = "moskowitz_2024"

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate Moskowitz Momentum Factor.

        Args:
            data: DataFrame with OHLCV columns (datetime, open, high, low, close, volume)

        Returns:
            DataFrame with 'factor_value' column
        """
        df = data.copy()

        if "close" not in df.columns:
            result = pd.DataFrame({"factor_value": [None]})
            return result

        lookback_days = 252
        skip_days = 21

        signal_value = df["close"].shift(skip_days) / df["close"].shift(lookback_days) - 1

        result = pd.DataFrame({"factor_value": signal_value})

        return result
