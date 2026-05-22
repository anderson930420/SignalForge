"""Factor protocol definition for SignalForge."""

from typing import Protocol, runtime_checkable

import pandas as pd


FACTOR_OUTPUT_COLUMNS = [
    "datetime",
    "symbol",
    "factor_name",
    "factor_value",
    "available_at",
]


def require_columns(
    data: pd.DataFrame,
    required_inputs: tuple[str, ...],
    factor_name: str,
) -> None:
    """Raise a clear error when factor input columns are missing."""
    missing = [column for column in required_inputs if column not in data.columns]
    if missing:
        raise ValueError(
            f"Missing required input columns for factor '{factor_name}': "
            f"{', '.join(missing)}"
        )


@runtime_checkable
class BaseAlphaFactor(Protocol):
    """Protocol for canonical factor implementations.

    All factor implementations must conform to this protocol.
    Factors must not output target_position, signal_binary, or performance metrics.
    SignalComposer is responsible for converting factor_value into signal_binary.
    """

    name: str
    version: str

    def required_inputs(self) -> tuple[str, ...]:
        """Return tuple of required input column names."""
        ...

    def compute(self, data: pd.DataFrame) -> pd.DataFrame:
        """Compute factor values from input data.

        Args:
            data: DataFrame with required input columns

        Returns:
            DataFrame with canonical factor output columns:
            datetime, symbol, factor_name, factor_value, available_at
        """
        ...


class FactorProtocol(BaseAlphaFactor, Protocol):
    """Legacy protocol alias for backward compatibility.

    Deprecated: use BaseAlphaFactor instead.
    """

    name: str
    source: str

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate factor values from OHLCV data.

        Args:
            data: DataFrame with OHLCV columns (datetime, open, high, low, close, volume)

        Returns:
            DataFrame with factor values (must include 'factor_value' column)
        """
        ...
