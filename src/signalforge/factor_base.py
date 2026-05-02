"""Factor protocol definition for SignalForge."""

from typing import Protocol

import pandas as pd


class FactorProtocol(Protocol):
    """Protocol for factor implementations.

    All factor implementations must conform to this protocol.
    """

    name: str
    source: str

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate factor values from OHLCV data.

        Args:
            data: DataFrame with OHLCV columns (datetime, open, high, low, close, volume)

        Returns:
            DataFrame with factor values (must include 'signal_value' column)
        """
        ...
