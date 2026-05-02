"""Artifact writing and deterministic file layout."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from signalforge.schemas import ExportError, SIGNAL_COLUMNS, SignalValidator


def export_signal_csv(
    df: pd.DataFrame,
    output_dir: Path,
    validate: bool = True,
) -> Path:
    """Export signal DataFrame to CSV.

    Args:
        df: DataFrame with signal data
        output_dir: Output directory
        validate: Whether to validate before export

    Returns:
        Path to exported CSV file

    Raises:
        ExportError: If export fails
        SignalValidationError: If validation fails
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    if validate:
        validator = SignalValidator()
        validator.validate_or_raise(df)

    filepath = output_dir / "signal.csv"

    df = df[SIGNAL_COLUMNS]

    try:
        df.to_csv(filepath, index=False, lineterminator="\n")
    except Exception as e:
        raise ExportError(f"Failed to export signal.csv: {e}")

    return filepath


def export_signal_contract_yaml(
    contract_data: dict[str, Any],
    output_dir: Path,
) -> Path:
    """Export signal contract to YAML.

    Args:
        contract_data: Contract metadata dict
        output_dir: Output directory

    Returns:
        Path to exported YAML file

    Raises:
        ExportError: If export fails
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    filepath = output_dir / "signal_contract.yaml"

    try:
        with open(filepath, "w") as f:
            yaml.dump(contract_data, f, default_flow_style=False)
    except Exception as e:
        raise ExportError(f"Failed to export signal_contract.yaml: {e}")

    return filepath


def export_data_quality_report(
    report_data: dict[str, Any],
    output_dir: Path,
) -> Path:
    """Export data quality report to JSON.

    Args:
        report_data: Quality report dict
        output_dir: Output directory

    Returns:
        Path to exported JSON file

    Raises:
        ExportError: If export fails
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    filepath = output_dir / "data_quality_report.json"

    try:
        with open(filepath, "w") as f:
            json.dump(report_data, f, indent=2, default=str)
    except Exception as e:
        raise ExportError(f"Failed to export data_quality_report.json: {e}")

    return filepath


def build_signal_contract(
    signal_name: str,
    source: str,
    factor_name: str,
    parameters: dict[str, Any],
    decision_rule: str,
    timing_rule: str,
    symbols: list[str],
    datetime_range: tuple[str, str],
    row_count: int,
    signal_value_stats: dict[str, float],
    signal_binary_stats: dict[str, int],
) -> dict[str, Any]:
    """Build signal contract YAML data structure.

    Args:
        signal_name: Name of the signal
        source: Source identifier
        factor_name: Factor name
        parameters: Factor parameters
        decision_rule: Decision rule description
        timing_rule: Timing rule description
        symbols: List of symbols
        datetime_range: Tuple of (start, end) ISO timestamps
        row_count: Number of signal rows
        signal_value_stats: Statistics for signal_value
        signal_binary_stats: Statistics for signal_binary

    Returns:
        Contract data dictionary
    """
    return {
        "signal_name": signal_name,
        "version": "1.0",
        "source": source,
        "factor": factor_name,
        "parameters": parameters,
        "decision_rule": decision_rule,
        "timing_rule": timing_rule,
        "schema_version": "1.0",
        "output_file": "signal.csv",
        "exported_at": datetime.now().isoformat() + "Z",
        "generator": "SignalForge",
        "signals": [
            {
                "signal_name": signal_name,
                "source": source,
                "symbols": symbols,
                "datetime_range": {
                    "start": datetime_range[0],
                    "end": datetime_range[1],
                },
                "row_count": row_count,
                "signal_value_stats": signal_value_stats,
                "signal_binary_stats": signal_binary_stats,
            }
        ],
    }


def build_data_quality_report(
    signal_df: pd.DataFrame,
    dataset_name: str = "unknown",
    source_type: str = "csv",
) -> dict[str, Any]:
    """Build data quality report JSON structure.

    Args:
        signal_df: Signal DataFrame
        dataset_name: Name of the dataset
        source_type: Type of data source

    Returns:
        Quality report dictionary
    """
    row_count = len(signal_df)
    symbols = signal_df["symbol"].unique().tolist() if "symbol" in signal_df.columns else []

    datetime_col = signal_df["datetime"] if "datetime" in signal_df.columns else pd.Series(dtype="datetime64[ns, UTC]")
    start_date = datetime_col.min().isoformat() if len(datetime_col) > 0 else None
    end_date = datetime_col.max().isoformat() if len(datetime_col) > 0 else None

    dup_cols = ["datetime", "symbol", "signal_name"]
    duplicate_rows = int(signal_df.duplicated(subset=dup_cols, keep=False).sum()) if all(c in signal_df.columns for c in dup_cols) else 0

    missing_values = int(signal_df.isnull().sum().sum())

    signal_value_stats = {}
    if "signal_value" in signal_df.columns:
        signal_value_stats = {
            "min": float(signal_df["signal_value"].min()) if not signal_df["signal_value"].isnull().all() else None,
            "max": float(signal_df["signal_value"].max()) if not signal_df["signal_value"].isnull().all() else None,
            "mean": float(signal_df["signal_value"].mean()) if not signal_df["signal_value"].isnull().all() else None,
            "null_count": int(signal_df["signal_value"].isnull().sum()),
        }

    signal_binary_stats = {}
    if "signal_binary" in signal_df.columns:
        signal_binary_stats = {
            "value_0_count": int((signal_df["signal_binary"] == 0).sum()),
            "value_1_count": int((signal_df["signal_binary"] == 1).sum()),
            "null_count": int(signal_df["signal_binary"].isnull().sum()),
        }

    return {
        "version": "1.0",
        "exported_at": datetime.now().isoformat() + "Z",
        "generator": "SignalForge",
        "dataset_name": dataset_name,
        "source_type": source_type,
        "symbol_count": len(symbols),
        "row_count": row_count,
        "start_date": start_date,
        "end_date": end_date,
        "duplicate_rows": duplicate_rows,
        "missing_values": missing_values,
        "warnings": [],
        "signals": [
            {
                "signal_value_stats": signal_value_stats,
                "signal_binary_stats": signal_binary_stats,
            }
        ] if row_count > 0 else [],
    }
