"""Passive data models and schema constants for SignalForge."""

from dataclasses import dataclass
from typing import Optional
import pandas as pd


SIGNAL_COLUMNS = [
    "datetime",
    "available_at",
    "symbol",
    "signal_name",
    "signal_value",
    "signal_binary",
    "source",
]


SIGNAL_COLUMN_TYPES = {
    "datetime": pd.Timestamp,
    "available_at": pd.Timestamp,
    "symbol": str,
    "signal_name": str,
    "signal_value": Optional[float],
    "signal_binary": int,
    "source": str,
}


OHLCV_COLUMNS = ["datetime", "open", "high", "low", "close", "volume"]


@dataclass
class SignalArtifact:
    datetime: pd.Timestamp
    available_at: pd.Timestamp
    symbol: str
    signal_name: str
    signal_value: Optional[float]
    signal_binary: int
    source: str


@dataclass
class DataQualityIssue:
    severity: str
    code: str
    message: str
    affected_rows: int


class DataQualityError(Exception):
    pass


class MissingColumnsError(DataQualityError):
    pass


class ExportError(Exception):
    pass


class SignalValidationError(Exception):
    pass


class SignalValidator:
    """Validate signal DataFrame against signal artifact contract."""

    REQUIRED_COLUMNS = SIGNAL_COLUMNS

    def validate(self, df: pd.DataFrame) -> list[str]:
        """Validate signal DataFrame.

        Args:
            df: Signal DataFrame to validate

        Returns:
            List of error messages (empty if valid)
        """
        errors = []

        if len(df.columns) != 7:
            errors.append(f"Expected 7 columns, got {len(df.columns)}")

        if list(df.columns) != self.REQUIRED_COLUMNS:
            errors.append(
                f"Column order mismatch: expected {self.REQUIRED_COLUMNS}, "
                f"got {list(df.columns)}"
            )

        if "signal_binary" in df.columns:
            invalid = ~df["signal_binary"].isin([0, 1])
            if invalid.any():
                errors.append("signal_binary contains values other than 0 or 1")

        if "available_at" in df.columns and "datetime" in df.columns:
            violations = df["available_at"] > df["datetime"]
            if violations.any():
                errors.append("available_at > datetime violations found")

        for col in ["datetime", "available_at", "symbol", "signal_name", "signal_binary", "source"]:
            if col in df.columns and df[col].isnull().any():
                errors.append(f"Null values found in required column: {col}")

        dup_cols = ["datetime", "symbol", "signal_name"]
        if all(c in df.columns for c in dup_cols):
            duplicates = df.duplicated(subset=dup_cols, keep=False)
            if duplicates.any():
                errors.append("Duplicate datetime-symbol-signal_name rows found")

        return errors

    def validate_or_raise(self, df: pd.DataFrame) -> None:
        """Validate and raise if errors found."""
        errors = self.validate(df)
        if errors:
            raise SignalValidationError("\n".join(errors))
