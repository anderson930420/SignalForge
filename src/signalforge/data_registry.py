"""Data loading, normalization, and quality checks for OHLCV market data."""

import pandas as pd

from signalforge.schemas import (
    OHLCV_COLUMNS,
    MissingColumnsError,
)


def local_ohlcv_csv(filepath: str, symbol: str | None = None) -> pd.DataFrame:
    """Load OHLCV data from local CSV file.

    Args:
        filepath: Path to CSV file with OHLCV data
        symbol: Optional symbol to inject if CSV doesn't contain it

    Returns:
        DataFrame with normalized OHLCV columns

    Raises:
        MissingColumnsError: If required OHLCV columns are absent
    """
    df = pd.read_csv(filepath)

    df.columns = df.columns.str.lower().str.strip()

    required = set(OHLCV_COLUMNS)
    present = set(df.columns)
    missing = required - present

    if missing:
        raise MissingColumnsError(
            f"Missing required columns: {missing}"
        )

    if "datetime" in df.columns:
        df["datetime"] = pd.to_datetime(df["datetime"], utc=True)

    if symbol is not None and "symbol" not in df.columns:
        df["symbol"] = symbol

    return df


def load_ohlcv_csv(filepath: str) -> pd.DataFrame:
    """Load OHLCV data from CSV file.

    Args:
        filepath: Path to CSV file with OHLCV data

    Returns:
        DataFrame with normalized OHLCV columns

    Raises:
        MissingColumnsError: If required OHLCV columns are absent
    """
    return local_ohlcv_csv(filepath, symbol=None)


def validate_ohlcv_quality(df: pd.DataFrame) -> list[dict]:
    """Validate OHLCV data quality.

    Args:
        df: DataFrame with OHLCV columns

    Returns:
        List of quality issue dictionaries
    """
    issues = []

    for col in ["open", "high", "low", "close", "volume"]:
        if col in df.columns:
            null_count = df[col].isnull().sum()
            if null_count > 0:
                issues.append({
                    "severity": "warning",
                    "code": "NULL_OHLCV",
                    "message": f"Null values in {col}",
                    "affected_rows": int(null_count),
                })

    if "high" in df.columns and "low" in df.columns:
        violations = (df["high"] < df["low"]).sum()
        if violations > 0:
            issues.append({
                "severity": "warning",
                "code": "PRICE_INTEGRITY_VIOLATION",
                "message": "high < low violations",
                "affected_rows": int(violations),
            })

    return issues
