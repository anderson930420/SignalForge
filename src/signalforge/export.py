"""Artifact writing and deterministic file layout."""

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

from signalforge.compatibility import (
    validate_signal_csv,
    validate_signal_market_date_alignment,
)
from signalforge.schemas import ExportError, SIGNAL_COLUMNS, SignalValidator
from signalforge.schemas import OHLCV_COLUMNS


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

    df_sorted = df.sort_values(
        by=["datetime", "symbol", "signal_name"],
        kind="mergesort",
    ).reset_index(drop=True)

    try:
        df_sorted.to_csv(filepath, index=False, lineterminator="\n")
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
            yaml.safe_dump(contract_data, f, default_flow_style=False, sort_keys=False)
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
    *,
    symbol: str | None = None,
    frequency: str = "daily",
    input_data: dict[str, Any] | None = None,
    compatibility: dict[str, Any] | None = None,
    version: str = "0.1.0",
    factor_version: str = "0.1.0",
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
        Contract data dictionary (deterministic - no volatile timestamps)
    """
    sorted_parameters = dict(sorted(parameters.items())) if parameters else {}

    return {
        "signal_name": signal_name,
        "version": version,
        "source": source,
        "factor": {
            "name": factor_name,
            "version": factor_version,
            "parameters": sorted_parameters,
        },
        "decision_rule": {
            "signal_binary": decision_rule,
        },
        "data": {
            "required_columns": ["datetime", "open", "high", "low", "close", "volume", "symbol"],
        },
        "timing": {
            "available_at_rule": timing_rule,
        },
        "output": {
            "file": "signal.csv",
            "schema_version": "0.1.0",
            "columns": SIGNAL_COLUMNS,
        },
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


def build_market_data_quality_report(
    market_data: pd.DataFrame,
    dataset_name: str = "unknown",
    source_type: str = "local_ohlcv_csv",
) -> dict[str, Any]:
    """Build market data quality report from normalized OHLCV data.

    Args:
        market_data: Normalized OHLCV market data DataFrame
        dataset_name: Name/path of the dataset
        source_type: Type of data source (default: local_ohlcv_csv)

    Returns:
        Quality report dictionary for source market data (deterministic - no volatile timestamps)
    """
    row_count = len(market_data)
    symbols = market_data["symbol"].unique().tolist() if "symbol" in market_data.columns else []

    datetime_col = market_data["datetime"] if "datetime" in market_data.columns else pd.Series(dtype="datetime64[ns, UTC]")
    start_date = datetime_col.min().isoformat() if len(datetime_col) > 0 else None
    end_date = datetime_col.max().isoformat() if len(datetime_col) > 0 else None

    dup_cols = ["datetime", "symbol"]
    duplicate_rows = int(market_data.duplicated(subset=dup_cols, keep=False).sum()) if all(c in market_data.columns for c in dup_cols) else 0

    missing_values = {}
    ohlcv_cols = ["open", "high", "low", "close", "volume"]
    for col in ohlcv_cols:
        if col in market_data.columns:
            missing_values[col] = int(market_data[col].isnull().sum())
        else:
            missing_values[col] = 0

    warnings = []
    for col in ohlcv_cols:
        if col in market_data.columns:
            null_count = market_data[col].isnull().sum()
            if null_count > 0:
                warnings.append({
                    "code": f"NULL_{col.upper()}",
                    "message": f"Null values in {col}",
                    "affected_rows": int(null_count),
                })

    if "high" in market_data.columns and "low" in market_data.columns:
        violations = (market_data["high"] < market_data["low"]).sum()
        if violations > 0:
            warnings.append({
                "code": "PRICE_INTEGRITY_VIOLATION",
                "message": "high < low violations",
                "affected_rows": int(violations),
            })

    if len(market_data) == 0:
        warnings.append({
            "code": "EMPTY_DATASET",
            "message": "Market data is empty",
            "affected_rows": 0,
        })

    warnings.sort(key=lambda w: w["code"])

    return {
        "version": "1.0",
        "generator": "SignalForge",
        "dataset_name": dataset_name,
        "source_type": source_type,
        "symbol_count": len(symbols),
        "row_count": row_count,
        "start_date": start_date,
        "end_date": end_date,
        "duplicate_rows": duplicate_rows,
        "missing_values": missing_values,
        "warnings": warnings,
        "point_in_time_correctness_claimed": False,
    }


def export_alphaforge_compatibility_package(
    market_data_df: pd.DataFrame,
    signal_df: pd.DataFrame,
    output_dir: Path,
    *,
    package_name: str = "alphaforge_compatibility_smoke_export",
    package_version: str = "1.0.0",
    generated_for: str | None = None,
    signal_name: str | None = None,
    source: str | None = None,
    factor_name: str | None = None,
    factor_params: dict[str, Any] | None = None,
    decision_rule: str = "signal_binary = 1 if signal_value > 0 else 0",
    timing_rule: str = "available_at <= datetime",
    schema_version: str = "1.0",
    alpha_forge_strategy: str = "custom_signal",
    expected_alpha_forge_execution_semantics: str = "legacy_close_to_close_lagged",
) -> dict[str, Path]:
    """Export a deterministic AlphaForge compatibility smoke package.

    Args:
        market_data_df: OHLCV market data used to build the package
        signal_df: Signal artifact rows to export
        output_dir: Package directory to write
        package_name: Deterministic package name
        package_version: Package version string
        generated_for: Optional package label; defaults to the output directory name
        signal_name: Optional signal name override
        source: Optional source override
        factor_name: Optional factor name override
        factor_params: Optional factor parameter payload
        decision_rule: Human-readable decision rule description
        timing_rule: Human-readable timing rule description
        schema_version: Contract schema version
        alpha_forge_strategy: AlphaForge strategy identifier
        expected_alpha_forge_execution_semantics: Expected AlphaForge semantics

    Returns:
        Mapping of exported artifact names to their file paths

    Raises:
        ExportError: If validation or export fails
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    market_data = _normalize_market_data(market_data_df)
    signals = _normalize_signal_data(signal_df)

    _validate_alphaforge_compatibility_inputs(market_data, signals)

    market_data_path = _export_market_data_csv(market_data, output_dir)
    signal_csv_path = export_signal_csv(signals, output_dir, validate=True)

    signal_dates = _sorted_unique_dates(signals["datetime"])
    start_date = signal_dates[0].date().isoformat()
    end_date = signal_dates[-1].date().isoformat()
    symbol = _single_unique_value(signals, "symbol")
    signal_name_value = signal_name or _single_unique_value(signals, "signal_name")
    source_value = source or _single_unique_value(signals, "source")
    factor_name_value = factor_name or signal_name_value
    factor_params_value = factor_params or {}
    package_label = generated_for or output_dir.name

    contract_data = {
        "signal_name": signal_name_value,
        "source": source_value,
        "factor": factor_name_value,
        "factor_params": factor_params_value,
        "decision_rule": decision_rule,
        "timing_rule": timing_rule,
        "schema_version": schema_version,
        "output_file": "signal.csv",
        "row_count": len(signals),
        "symbol": symbol,
        "datetime_start": start_date,
        "datetime_end": end_date,
        "generator": "SignalForge",
    }

    data_quality_report = {
        "source_type": "local_ohlcv_csv",
        "symbol_count": int(signals["symbol"].nunique()),
        "row_count": len(signals),
        "start_date": start_date,
        "end_date": end_date,
        "duplicate_rows": 0,
        "missing_values": int(market_data.isnull().sum().sum() + signals.isnull().sum().sum()),
        "warnings": [],
        "generator": "SignalForge",
    }

    manifest_data = {
        "package_name": package_name,
        "package_version": package_version,
        "generator": "SignalForge",
        "generated_for": package_label,
        "symbol": symbol,
        "start_date": start_date,
        "end_date": end_date,
        "market_data_file": "market_data.csv",
        "signal_file": "signal.csv",
        "signal_contract_file": "signal_contract.yaml",
        "data_quality_report_file": "data_quality_report.json",
        "row_count": len(signals),
        "schema_version": schema_version,
        "alpha_forge_strategy": alpha_forge_strategy,
        "expected_alpha_forge_execution_semantics": expected_alpha_forge_execution_semantics,
        "contains_backtest_results": False,
        "contains_performance_metrics": False,
    }

    readme_text = _build_alphaforge_compatibility_readme(
        package_label=package_label,
        package_path=output_dir,
        start_date=start_date,
        end_date=end_date,
        development_end=signal_dates[max(0, (len(signal_dates) // 2) - 1)].date().isoformat(),
        holdout_start=signal_dates[min(len(signal_dates) - 1, max(1, len(signal_dates) // 2))].date().isoformat(),
        signal_name=signal_name_value,
        source=source_value,
        factor_name=factor_name_value,
        decision_rule=decision_rule,
        timing_rule=timing_rule,
    )

    signal_contract_path = export_signal_contract_yaml(contract_data, output_dir)
    quality_report_path = export_data_quality_report(data_quality_report, output_dir)
    manifest_path = _export_manifest_json(manifest_data, output_dir)
    readme_path = _export_readme(readme_text, output_dir)

    _validate_alphaforge_compatibility_package(
        output_dir=output_dir,
        market_data_path=market_data_path,
        signal_csv_path=signal_csv_path,
        signal_contract_path=signal_contract_path,
        quality_report_path=quality_report_path,
        manifest_path=manifest_path,
        readme_path=readme_path,
        market_data_df=market_data,
        signal_df=signals,
        readme_text=readme_text,
    )

    return {
        "market_data.csv": market_data_path,
        "signal.csv": signal_csv_path,
        "signal_contract.yaml": signal_contract_path,
        "data_quality_report.json": quality_report_path,
        "manifest.json": manifest_path,
        "README.md": readme_path,
    }


def _normalize_market_data(df: pd.DataFrame) -> pd.DataFrame:
    normalized = df.copy()
    missing = [column for column in OHLCV_COLUMNS if column not in normalized.columns]
    if missing:
        raise ExportError(f"Missing required market data columns: {missing}")

    normalized = normalized[OHLCV_COLUMNS].copy()
    normalized["datetime"] = pd.to_datetime(normalized["datetime"], utc=True)
    normalized = normalized.sort_values("datetime").reset_index(drop=True)
    return normalized


def _normalize_signal_data(df: pd.DataFrame) -> pd.DataFrame:
    normalized = df.copy()
    normalized["datetime"] = pd.to_datetime(normalized["datetime"], utc=True)
    normalized["available_at"] = pd.to_datetime(normalized["available_at"], utc=True)
    normalized = normalized[SIGNAL_COLUMNS].copy()
    normalized = normalized.sort_values(
        by=["datetime", "symbol", "signal_name"],
        kind="mergesort",
    ).reset_index(drop=True)
    return normalized


def _sorted_unique_dates(series: pd.Series) -> list[pd.Timestamp]:
    dates = pd.Index(pd.to_datetime(series, utc=True).unique())
    return list(dates.sort_values())


def _single_unique_value(df: pd.DataFrame, column: str) -> Any:
    unique_values = df[column].dropna().unique()
    if len(unique_values) != 1:
        raise ExportError(f"Expected exactly one unique value for {column}, got {len(unique_values)}")
    return unique_values[0]


def _export_market_data_csv(df: pd.DataFrame, output_dir: Path) -> Path:
    filepath = output_dir / "market_data.csv"
    try:
        df.to_csv(filepath, index=False, lineterminator="\n")
    except Exception as e:
        raise ExportError(f"Failed to export market_data.csv: {e}")
    return filepath


def _export_manifest_json(data: dict[str, Any], output_dir: Path) -> Path:
    filepath = output_dir / "manifest.json"
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, sort_keys=True)
            f.write("\n")
    except Exception as e:
        raise ExportError(f"Failed to export manifest.json: {e}")
    return filepath


def _export_readme(text: str, output_dir: Path) -> Path:
    filepath = output_dir / "README.md"
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(text)
            if not text.endswith("\n"):
                f.write("\n")
    except Exception as e:
        raise ExportError(f"Failed to export README.md: {e}")
    return filepath


def _build_alphaforge_compatibility_readme(
    *,
    package_label: str,
    package_path: Path,
    start_date: str,
    end_date: str,
    development_end: str,
    holdout_start: str,
    signal_name: str,
    source: str,
    factor_name: str,
    decision_rule: str,
    timing_rule: str,
) -> str:
    readme = f"""# AlphaForge Compatibility Smoke Export Package

This package is a deterministic SignalForge smoke export bundle for AlphaForge custom_signal validation.

SignalForge generated the signal artifacts in this package.
AlphaForge should validate and backtest the package contents.
AlphaForge must not import SignalForge internals.

## Package

- Package: `{package_label}`
- Location: `{package_path}`
- Signal: `{signal_name}`
- Source: `{source}`
- Factor: `{factor_name}`
- Decision rule: `{decision_rule}`
- Timing rule: `{timing_rule}`

## Files

- `market_data.csv`
- `signal.csv`
- `signal_contract.yaml`
- `data_quality_report.json`
- `manifest.json`
- `README.md`

## AlphaForge Validation

Use the package with:

```bash
alphaforge research-validate --strategy custom_signal --data {package_path}/market_data.csv --signal-file {package_path}/signal.csv
```

## Split Dates

- Development: {start_date} to {development_end}
- Holdout: {holdout_start} to {end_date}

Both splits contain at least one row in this package.
"""
    return readme.strip() + "\n"


def _validate_alphaforge_compatibility_inputs(
    market_data_df: pd.DataFrame,
    signal_df: pd.DataFrame,
) -> None:
    if len(market_data_df) <= 1:
        raise ExportError("market_data.csv must contain more than one row")
    if len(signal_df) <= 1:
        raise ExportError("signal.csv must contain more than one row")

    market_columns = list(market_data_df.columns)
    if market_columns != OHLCV_COLUMNS:
        raise ExportError(
            f"market_data.csv columns must be {OHLCV_COLUMNS}, got {market_columns}"
        )

    signal_errors = validate_signal_csv(signal_df)
    if signal_errors:
        raise ExportError("Invalid signal.csv:\n" + "\n".join(signal_errors))

    alignment_errors = validate_signal_market_date_alignment(signal_df, market_data_df)
    if alignment_errors:
        raise ExportError("Invalid signal.csv date alignment:\n" + "\n".join(alignment_errors))

    required_market = ["open", "high", "low", "close"]
    for column in required_market:
        values = market_data_df[column]
        if not np.isfinite(values).all():
            raise ExportError(f"market_data.csv column {column} must contain finite values")
        if (values <= 0).any():
            raise ExportError(f"market_data.csv column {column} must contain positive values")

    if (market_data_df["high"] < market_data_df["low"]).any():
        raise ExportError("market_data.csv high must be >= low")
    if (market_data_df["high"] < market_data_df["open"]).any():
        raise ExportError("market_data.csv high must be >= open")
    if (market_data_df["high"] < market_data_df["close"]).any():
        raise ExportError("market_data.csv high must be >= close")
    if (market_data_df["low"] > market_data_df["open"]).any():
        raise ExportError("market_data.csv low must be <= open")
    if (market_data_df["low"] > market_data_df["close"]).any():
        raise ExportError("market_data.csv low must be <= close")
    if market_data_df["volume"].isnull().any():
        raise ExportError("market_data.csv volume must be present")

    market_dates = set(market_data_df["datetime"])
    signal_dates = set(signal_df["datetime"])
    if market_dates != signal_dates:
        raise ExportError("market_data.csv datetime set must exactly match signal.csv datetime set")

    if not signal_df["signal_binary"].isin([0, 1]).all():
        raise ExportError("signal.csv signal_binary must contain only 0 or 1")
    if (signal_df["available_at"] > signal_df["datetime"]).any():
        raise ExportError("signal.csv available_at must be <= datetime")
    if signal_df.duplicated(subset=["datetime", "symbol", "signal_name"], keep=False).any():
        raise ExportError("signal.csv must not contain duplicate datetime-symbol-signal_name rows")

    if len(signal_df) <= 1:
        raise ExportError("signal.csv must contain more than one row")


def _validate_alphaforge_compatibility_package(
    *,
    output_dir: Path,
    market_data_path: Path,
    signal_csv_path: Path,
    signal_contract_path: Path,
    quality_report_path: Path,
    manifest_path: Path,
    readme_path: Path,
    market_data_df: pd.DataFrame,
    signal_df: pd.DataFrame,
    readme_text: str,
) -> None:
    expected_files = {
        "market_data.csv",
        "signal.csv",
        "signal_contract.yaml",
        "data_quality_report.json",
        "manifest.json",
        "README.md",
    }
    present_files = {path.name for path in output_dir.iterdir() if path.is_file()}
    if present_files != expected_files:
        raise ExportError(
            f"Package files must be exactly {sorted(expected_files)}, got {sorted(present_files)}"
        )

    if not market_data_path.exists() or not signal_csv_path.exists():
        raise ExportError("Expected package CSV files were not created")
    if not signal_contract_path.exists() or not quality_report_path.exists():
        raise ExportError("Expected package metadata files were not created")
    if not manifest_path.exists() or not readme_path.exists():
        raise ExportError("Expected package documentation files were not created")

    parsed_signal = pd.read_csv(signal_csv_path)
    parsed_market = pd.read_csv(market_data_path)
    parsed_signal["datetime"] = pd.to_datetime(parsed_signal["datetime"], utc=True)
    parsed_signal["available_at"] = pd.to_datetime(parsed_signal["available_at"], utc=True)
    parsed_market["datetime"] = pd.to_datetime(parsed_market["datetime"], utc=True)

    if list(parsed_market.columns) != OHLCV_COLUMNS:
        raise ExportError("market_data.csv columns were not preserved")
    if list(parsed_signal.columns) != SIGNAL_COLUMNS:
        raise ExportError("signal.csv columns were not preserved")

    if set(parsed_market["datetime"]) != set(parsed_signal["datetime"]):
        raise ExportError("market_data.csv and signal.csv datetime sets diverged after export")

    contract_loaded = yaml.safe_load(signal_contract_path.read_text(encoding="utf-8"))
    report_loaded = json.loads(quality_report_path.read_text(encoding="utf-8"))
    manifest_loaded = json.loads(manifest_path.read_text(encoding="utf-8"))

    expected_contract_keys = {
        "signal_name",
        "source",
        "factor",
        "factor_params",
        "decision_rule",
        "timing_rule",
        "schema_version",
        "output_file",
        "row_count",
        "symbol",
        "datetime_start",
        "datetime_end",
        "generator",
    }
    if set(contract_loaded) != expected_contract_keys:
        raise ExportError("signal_contract.yaml must contain the required smoke-package keys")

    expected_report_keys = {
        "source_type",
        "symbol_count",
        "row_count",
        "start_date",
        "end_date",
        "duplicate_rows",
        "missing_values",
        "warnings",
        "generator",
    }
    if set(report_loaded) != expected_report_keys:
        raise ExportError("data_quality_report.json must contain the required smoke-package keys")

    expected_manifest_keys = {
        "package_name",
        "package_version",
        "generator",
        "generated_for",
        "symbol",
        "start_date",
        "end_date",
        "market_data_file",
        "signal_file",
        "signal_contract_file",
        "data_quality_report_file",
        "row_count",
        "schema_version",
        "alpha_forge_strategy",
        "expected_alpha_forge_execution_semantics",
        "contains_backtest_results",
        "contains_performance_metrics",
    }
    if set(manifest_loaded) != expected_manifest_keys:
        raise ExportError("manifest.json must contain the required smoke-package keys")

    if manifest_loaded["contains_backtest_results"] is not False:
        raise ExportError("manifest.json contains_backtest_results must be False")
    if manifest_loaded["contains_performance_metrics"] is not False:
        raise ExportError("manifest.json contains_performance_metrics must be False")

    if contract_loaded["row_count"] != len(parsed_signal):
        raise ExportError("signal_contract.yaml row_count must match signal.csv row count")
    if report_loaded["row_count"] != len(parsed_signal):
        raise ExportError("data_quality_report.json row_count must match signal.csv row count")
    if manifest_loaded["row_count"] != len(parsed_signal):
        raise ExportError("manifest.json row_count must match signal.csv row count")
    if manifest_loaded["alpha_forge_strategy"] != "custom_signal":
        raise ExportError("manifest.json alpha_forge_strategy must be custom_signal")
    if manifest_loaded["expected_alpha_forge_execution_semantics"] != "legacy_close_to_close_lagged":
        raise ExportError(
            "manifest.json expected_alpha_forge_execution_semantics must be legacy_close_to_close_lagged"
        )
    if "alphaforge research-validate --strategy custom_signal" not in readme_text:
        raise ExportError("README.md must document the AlphaForge research-validate command")
    if "market_data.csv" not in readme_text or "signal.csv" not in readme_text:
        raise ExportError("README.md must reference market_data.csv and signal.csv")

    if contract_loaded["generator"] != "SignalForge":
        raise ExportError("signal_contract.yaml generator must be SignalForge")
    if report_loaded["generator"] != "SignalForge":
        raise ExportError("data_quality_report.json generator must be SignalForge")
    if manifest_loaded["generator"] != "SignalForge":
        raise ExportError("manifest.json generator must be SignalForge")
