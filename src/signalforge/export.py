"""Artifact writing and deterministic file layout."""

import json
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
