"""Pure AlphaForge-compatible schema validation."""

from typing import Any

import pandas as pd


class CompatibilityError(Exception):
    pass


def validate_signal_csv(df: pd.DataFrame) -> list[str]:
    """Validate signal.csv schema.

    Args:
        df: DataFrame to validate

    Returns:
        List of error messages (empty if valid)
    """
    errors = []

    expected_columns = [
        "datetime",
        "available_at",
        "symbol",
        "signal_name",
        "signal_value",
        "signal_binary",
        "source",
    ]

    if len(df.columns) != 7:
        errors.append(f"Expected 7 columns, got {len(df.columns)}")

    if list(df.columns) != expected_columns:
        errors.append(f"Column order mismatch: expected {expected_columns}, got {list(df.columns)}")

    if "signal_binary" in df.columns:
        invalid_binary = ~df["signal_binary"].isin([0, 1])
        if invalid_binary.any():
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


def validate_signal_market_date_alignment(
    signal_df: pd.DataFrame,
    market_df: pd.DataFrame,
) -> list[str]:
    """Validate that signal rows align one-to-one with market dates."""
    errors = []

    if "datetime" not in signal_df.columns:
        errors.append("signal.csv missing datetime column")
        return errors
    if "datetime" not in market_df.columns:
        errors.append("market data missing datetime column")
        return errors

    signal_dates = pd.to_datetime(signal_df["datetime"], utc=True).tolist()
    market_dates = pd.to_datetime(market_df["datetime"], utc=True).tolist()

    if signal_dates != market_dates:
        errors.append("signal dates must exactly match selected OHLCV market dates")

    return errors


def validate_signal_contract_yaml(data: dict[str, Any]) -> list[str]:
    """Validate signal_contract.yaml schema.

    Args:
        data: Contract data dict

    Returns:
        List of error messages (empty if valid)
    """
    errors = []

    required_keys = [
        "signal_name",
        "source",
        "version",
        "exported_at",
        "generator",
        "signals",
        "compatibility",
    ]
    for key in required_keys:
        if key not in data:
            errors.append(f"Missing required key: {key}")

    if "generator" in data and data["generator"] != "SignalForge":
        errors.append(f"Expected generator 'SignalForge', got '{data['generator']}'")

    if "compatibility" in data:
        compatibility = data["compatibility"]
        expected = {
            "alphaforge_strategy": "custom_signal",
            "execution_semantics": "legacy_close_to_close_lagged",
            "target_position_rule": "target_position = float(signal_binary)",
            "supports_shorting": False,
            "supports_leverage": False,
        }
        if not isinstance(compatibility, dict):
            errors.append("compatibility must be a dict")
        else:
            for key, value in expected.items():
                if key not in compatibility:
                    errors.append(f"Missing compatibility key: {key}")
                elif compatibility[key] != value:
                    errors.append(f"Unexpected compatibility value for {key}")

    if "signals" in data:
        if not isinstance(data["signals"], list):
            errors.append("signals must be a list")
        elif len(data["signals"]) == 0:
            errors.append("signals must be non-empty")

    return errors


def validate_cross_artifacts(
    signal_df: pd.DataFrame,
    contract_data: dict[str, Any],
) -> list[str]:
    """Validate consistency between signal.csv and signal_contract.yaml.

    Args:
        signal_df: Signal DataFrame
        contract_data: Contract data dict

    Returns:
        List of error messages (empty if valid)
    """
    errors = []

    if "signals" in contract_data and len(contract_data["signals"]) > 0:
        for entry in contract_data["signals"]:
            if "datetime_range" in entry:
                dr = entry["datetime_range"]
                if "start" in dr and "end" in dr:
                    sig_min = signal_df["datetime"].min()
                    sig_max = signal_df["datetime"].max()
                    if pd.Timestamp(dr["start"]) > sig_min:
                        errors.append("Contract datetime_range start mismatch")
                    if pd.Timestamp(dr["end"]) < sig_max:
                        errors.append("Contract datetime_range end mismatch")

    return errors
