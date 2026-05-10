"""Moskowitz Momentum Factor implementation.

Based on Moskowitz, Ostdie, and Wells (2024):
"Into the Darkness: An Empirical Investigation of Dark Matter Returns"

Formula: factor_value[t] = close[t - skip_days] / close[t - lookback_days] - 1

Parameters:
- lookback_days = 252 (12 months of trading days)
- skip_days = 21 (1 month of trading days)
"""


import pandas as pd

from signalforge.factor_base import BaseAlphaFactor, FACTOR_OUTPUT_COLUMNS


class MoskowitzMomentumFactor(BaseAlphaFactor):
    """Moskowitz Momentum Factor implementation."""

    name: str = "moskowitz_momentum"
    version: str = "0.1.0"

    def required_inputs(self) -> tuple[str, ...]:
        """Return required input columns."""
        return ("datetime", "close")

    def compute(self, data: pd.DataFrame) -> pd.DataFrame:
        """Compute Moskowitz Momentum Factor.

        Args:
            data: DataFrame with OHLCV columns (datetime, open, high, low, close, volume)

        Returns:
            DataFrame with canonical factor output columns:
            datetime, symbol, factor_name, factor_value, available_at
        """
        df = data.copy()

        if "close" not in df.columns:
            result = pd.DataFrame({col: [None] for col in FACTOR_OUTPUT_COLUMNS})
            return result

        lookback_days = 252
        skip_days = 21

        factor_value = df["close"].shift(skip_days) / df["close"].shift(lookback_days) - 1

        symbol = df["symbol"].iloc[0] if "symbol" in df.columns else None

        result = pd.DataFrame({
            "datetime": df["datetime"].values,
            "symbol": symbol,
            "factor_name": self.name,
            "factor_value": factor_value.values,
            "available_at": df["datetime"].values,
        })

        return result[FACTOR_OUTPUT_COLUMNS]

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate factor values (legacy interface).

        Args:
            data: DataFrame with OHLCV columns

        Returns:
            DataFrame with 'factor_value' column (legacy format)
        """
        df = data.copy()

        if "close" not in df.columns:
            result = pd.DataFrame({"factor_value": [None]})
            return result

        lookback_days = 252
        skip_days = 21

        factor_value = df["close"].shift(skip_days) / df["close"].shift(lookback_days) - 1

        result = pd.DataFrame({"factor_value": factor_value})

        return result
