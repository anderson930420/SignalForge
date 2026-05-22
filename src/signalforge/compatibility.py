"""Pure AlphaForge-compatible schema validation."""

from typing import Any

import pandas as pd

from signalforge.schemas import SIGNAL_COLUMNS


class CompatibilityError(Exception):
    pass


def normalize_declared_daily_trading_date(values: pd.Series | Any) -> pd.Series | pd.Timestamp:
    """Normalize daily datetime-like values by their declared calendar date.

    Offset-aware values keep their written calendar date instead of being
    converted through UTC before daily alignment.
    """
    if isinstance(values, pd.Series):
        return values.apply(_normalize_declared_daily_trading_date_scalar)

    return _normalize_declared_daily_trading_date_scalar(values)


def _normalize_declared_daily_trading_date_scalar(value: Any) -> pd.Timestamp:
    if pd.isna(value):
        raise ValueError("Invalid declared daily trading date: null value")

    try:
        parsed = pd.Timestamp(value)
    except Exception as exc:
        raise ValueError(f"Invalid declared daily trading date: {value!r}") from exc

    if pd.isna(parsed):
        raise ValueError(f"Invalid declared daily trading date: {value!r}")

    return pd.Timestamp(parsed.date())


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

    normalized_datetime = None
    normalized_available_at = None
    if "available_at" in df.columns and "datetime" in df.columns:
        try:
            normalized_datetime = normalize_declared_daily_trading_date(df["datetime"])
            normalized_available_at = normalize_declared_daily_trading_date(df["available_at"])
        except ValueError as exc:
            errors.append(f"Invalid datetime or available_at value: {exc}")
        else:
            violations = normalized_available_at > normalized_datetime
            if violations.any():
                errors.append("available_at > datetime violations found")

    for col in ["datetime", "available_at", "symbol", "signal_name", "signal_binary", "source"]:
        if col in df.columns and df[col].isnull().any():
            errors.append(f"Null values found in required column: {col}")

    dup_cols = ["datetime", "symbol", "signal_name"]
    if all(c in df.columns for c in dup_cols):
        duplicate_df = df[dup_cols].copy()
        if normalized_datetime is not None:
            duplicate_df["datetime"] = normalized_datetime
        duplicates = duplicate_df.duplicated(subset=dup_cols, keep=False)
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

    try:
        signal_dates = normalize_declared_daily_trading_date(signal_df["datetime"]).tolist()
        market_dates = normalize_declared_daily_trading_date(market_df["datetime"]).tolist()
    except ValueError as exc:
        errors.append(f"Invalid datetime value for date alignment: {exc}")
        return errors

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
        "version",
        "source",
        "factor",
        "decision_rule",
        "data",
        "timing",
        "output",
    ]
    for key in required_keys:
        if key not in data:
            errors.append(f"Missing required key: {key}")

    factor = data.get("factor")
    if not isinstance(factor, dict):
        errors.append("factor must be a dict")
    else:
        for key in ["name", "version", "parameters"]:
            if key not in factor:
                errors.append(f"Missing factor key: {key}")

    decision_rule = data.get("decision_rule")
    if not isinstance(decision_rule, dict):
        errors.append("decision_rule must be a dict")
    elif "signal_binary" not in decision_rule:
        errors.append("Missing decision_rule key: signal_binary")

    data_section = data.get("data")
    if not isinstance(data_section, dict):
        errors.append("data must be a dict")
    else:
        required_columns = data_section.get("required_columns")
        expected_ohlcv_columns = ["datetime", "open", "high", "low", "close", "volume", "symbol"]
        if not isinstance(required_columns, list):
            errors.append("data.required_columns must be a list")
        else:
            missing_columns = [col for col in expected_ohlcv_columns if col not in required_columns]
            if missing_columns:
                errors.append(f"data.required_columns missing required columns: {missing_columns}")

    timing = data.get("timing")
    if not isinstance(timing, dict):
        errors.append("timing must be a dict")
    elif "available_at_rule" not in timing:
        errors.append("Missing timing key: available_at_rule")

    output = data.get("output")
    if not isinstance(output, dict):
        errors.append("output must be a dict")
    else:
        if output.get("file") != "signal.csv":
            errors.append("output.file must equal signal.csv")
        if output.get("schema_version") != "0.1.0":
            errors.append("output.schema_version must equal 0.1.0")
        if output.get("columns") != SIGNAL_COLUMNS:
            errors.append(f"output.columns must equal {SIGNAL_COLUMNS}")

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

    output = contract_data.get("output")
    contract_columns = output.get("columns") if isinstance(output, dict) else None
    if contract_columns is None:
        errors.append("Contract missing output.columns")
    elif list(signal_df.columns) != contract_columns:
        errors.append(f"signal.csv columns do not match contract output.columns: {contract_columns}")

    contract_signal_name = contract_data.get("signal_name")
    if contract_signal_name is not None and "signal_name" in signal_df.columns:
        signal_names = set(signal_df["signal_name"].dropna().unique())
        if signal_names != {contract_signal_name}:
            errors.append("signal.csv signal_name values do not match contract signal_name")

    contract_source = contract_data.get("source")
    if contract_source is not None and "source" in signal_df.columns:
        sources = set(signal_df["source"].dropna().unique())
        if sources != {contract_source}:
            errors.append("signal.csv source values do not match contract source")

    return errors
