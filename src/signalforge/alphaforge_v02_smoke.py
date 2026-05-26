"""Deterministic AlphaForge v0.2 compatibility smoke package.

This module exports local files that prove SignalForge can produce the v0.2
signal contract expected by AlphaForge's custom_signal loader and signed
long/short runtime.

It intentionally does not import or execute AlphaForge.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from signalforge.compatibility import normalize_declared_daily_trading_date, validate_signal_market_date_alignment
from signalforge.export import build_market_data_quality_report, export_data_quality_report
from signalforge.schemas import ExportError, OHLCV_COLUMNS
from signalforge.signal_semantics import SIGNAL_CONTRACT_V02, V02_SIGNAL_COLUMNS, validate_v02_signal_frame

ALPHAFORGE_CUSTOM_SIGNAL_VERSION = "v0.2"
ALPHAFORGE_SIGNED_EXECUTION_SEMANTICS = "signed_close_to_close_lagged"
ALPHAFORGE_CUSTOM_SIGNAL_STRATEGY = "custom_signal"

V02_SMOKE_PACKAGE_FILES = (
    "market_data.csv",
    "signal.csv",
    "signal_contract.yaml",
    "data_quality_report.json",
    "manifest.json",
    "README.md",
)


def build_demo_market_data() -> pd.DataFrame:
    """Build deterministic single-symbol OHLCV data for compatibility smoke tests."""
    return pd.DataFrame(
        {
            "datetime": ["2025-01-02", "2025-01-03", "2025-01-06", "2025-01-07"],
            "open": [100.0, 101.0, 99.0, 100.0],
            "high": [102.0, 102.0, 101.0, 101.0],
            "low": [99.0, 98.0, 98.0, 99.0],
            "close": [101.0, 99.0, 100.0, 100.5],
            "volume": [1000, 1100, 1200, 1300],
        }
    )


def build_demo_v02_signal() -> pd.DataFrame:
    """Build deterministic v0.2 signal rows aligned with demo market data."""
    return pd.DataFrame(
        {
            "datetime": ["2025-01-02", "2025-01-03", "2025-01-06", "2025-01-07"],
            "available_at": ["2025-01-02", "2025-01-03", "2025-01-06", "2025-01-07"],
            "symbol": ["SFDEMO", "SFDEMO", "SFDEMO", "SFDEMO"],
            "signal_name": ["sf_v02_demo", "sf_v02_demo", "sf_v02_demo", "sf_v02_demo"],
            "score": [0.0, 1.25, -1.0, 0.0],
            "direction": [0, 1, -1, 0],
            "target_weight": [0.0, 1.0, -1.0, 0.0],
            "source": ["SignalForge", "SignalForge", "SignalForge", "SignalForge"],
        }
    )


def export_alphaforge_v02_compatibility_package(
    market_data_df: pd.DataFrame,
    signal_df: pd.DataFrame,
    output_dir: Path,
    *,
    package_name: str = "alphaforge_v02_compatibility_smoke_export",
    package_version: str = "1.0.0",
    generated_for: str | None = None,
    factor_name: str = "sf_v02_demo_factor",
    factor_version: str = "0.1.0",
    factor_params: dict[str, Any] | None = None,
) -> dict[str, Path]:
    """Export a deterministic AlphaForge-compatible v0.2 smoke package."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    market_data = _normalize_market_data(market_data_df)
    signals = _normalize_v02_signal(signal_df)
    _validate_v02_package_inputs(market_data, signals)

    symbol = _single_unique_value(signals, "symbol")
    signal_name = _single_unique_value(signals, "signal_name")
    source = _single_unique_value(signals, "source")
    dates = _sorted_unique_dates(signals["datetime"])
    start_date = dates[0].date().isoformat()
    end_date = dates[-1].date().isoformat()
    split_index = max(0, (len(dates) // 2) - 1)
    development_end = dates[split_index].date().isoformat()
    holdout_start = dates[min(len(dates) - 1, split_index + 1)].date().isoformat()
    package_label = generated_for or output_dir.name

    market_path = _write_csv(market_data, output_dir / "market_data.csv")
    signal_path = _write_csv(signals, output_dir / "signal.csv")

    market_data_for_report = market_data.copy()
    market_data_for_report["symbol"] = symbol
    data_quality_report = build_market_data_quality_report(
        market_data=market_data_for_report,
        dataset_name="market_data.csv",
        source_type="local_ohlcv_csv",
    )
    quality_path = export_data_quality_report(data_quality_report, output_dir)

    contract = _build_v02_contract(
        signal_name=signal_name,
        source=source,
        factor_name=factor_name,
        factor_version=factor_version,
        factor_params=factor_params or {},
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        row_count=len(signals),
    )
    contract_path = _write_yaml(contract, output_dir / "signal_contract.yaml")

    manifest = _build_manifest(
        package_name=package_name,
        package_version=package_version,
        package_label=package_label,
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        row_count=len(signals),
    )
    manifest_path = _write_json(manifest, output_dir / "manifest.json")

    readme_path = _write_text(
        _build_readme(
            package_label=package_label,
            start_date=start_date,
            end_date=end_date,
            development_end=development_end,
            holdout_start=holdout_start,
            signal_name=signal_name,
            source=source,
            factor_name=factor_name,
        ),
        output_dir / "README.md",
    )

    return {
        "market_data.csv": market_path,
        "signal.csv": signal_path,
        "signal_contract.yaml": contract_path,
        "data_quality_report.json": quality_path,
        "manifest.json": manifest_path,
        "README.md": readme_path,
    }


def export_demo_alphaforge_v02_compatibility_package(output_dir: Path) -> dict[str, Path]:
    """Export the built-in deterministic v0.2 compatibility smoke package."""
    return export_alphaforge_v02_compatibility_package(
        build_demo_market_data(),
        build_demo_v02_signal(),
        output_dir,
    )


def _normalize_market_data(df: pd.DataFrame) -> pd.DataFrame:
    missing = [column for column in OHLCV_COLUMNS if column not in df.columns]
    if missing:
        raise ExportError(f"Missing required market data columns: {missing}")
    normalized = df.loc[:, OHLCV_COLUMNS].copy()
    normalized["datetime"] = normalize_declared_daily_trading_date(normalized["datetime"])
    return normalized.sort_values("datetime").reset_index(drop=True)


def _normalize_v02_signal(df: pd.DataFrame) -> pd.DataFrame:
    signal = validate_v02_signal_frame(df).copy()
    signal["datetime"] = normalize_declared_daily_trading_date(signal["datetime"])
    signal["available_at"] = normalize_declared_daily_trading_date(signal["available_at"])
    signal = validate_v02_signal_frame(signal.loc[:, list(V02_SIGNAL_COLUMNS)])
    return signal.sort_values(["datetime", "symbol", "signal_name"], kind="mergesort").reset_index(drop=True)


def _validate_v02_package_inputs(market_data: pd.DataFrame, signals: pd.DataFrame) -> None:
    if len(market_data) <= 1:
        raise ExportError("market_data.csv must contain more than one row")
    if len(signals) <= 1:
        raise ExportError("signal.csv must contain more than one row")

    alignment_errors = validate_signal_market_date_alignment(signals, market_data)
    if alignment_errors:
        raise ExportError("Invalid v0.2 signal date alignment:\n" + "\n".join(alignment_errors))

    if set(market_data["datetime"]) != set(signals["datetime"]):
        raise ExportError("market_data.csv datetime set must exactly match signal.csv datetime set")
    if signals["target_weight"].lt(-1.0).any() or signals["target_weight"].gt(1.0).any():
        raise ExportError("v0.2 target_weight must be within [-1.0, 1.0]")
    if not signals["direction"].isin([-1, 0, 1]).all():
        raise ExportError("v0.2 direction must be ternary")


def _build_v02_contract(
    *,
    signal_name: str,
    source: str,
    factor_name: str,
    factor_version: str,
    factor_params: dict[str, Any],
    symbol: str,
    start_date: str,
    end_date: str,
    row_count: int,
) -> dict[str, Any]:
    return {
        "signal_name": signal_name,
        "version": "0.2.0",
        "source": source,
        "factor": {
            "name": factor_name,
            "version": factor_version,
            "parameters": dict(sorted(factor_params.items())) if factor_params else {},
        },
        "decision_rule": {
            "score": "SignalForge producer score",
            "direction": "sign(score)",
            "target_weight": "signed no-leverage target exposure consumed by AlphaForge custom_signal v0.2",
        },
        "data": {
            "required_columns": ["datetime", "open", "high", "low", "close", "volume", "symbol"],
        },
        "timing": {
            "available_at_rule": "same declared daily trading date as datetime for deterministic smoke data",
        },
        "output": {
            "file": "signal.csv",
            "schema_version": SIGNAL_CONTRACT_V02,
            "columns": list(V02_SIGNAL_COLUMNS),
            "row_count": row_count,
        },
        "compatibility": {
            "alphaforge_strategy": ALPHAFORGE_CUSTOM_SIGNAL_STRATEGY,
            "alphaforge_custom_signal_version": ALPHAFORGE_CUSTOM_SIGNAL_VERSION,
            "expected_execution_semantics": ALPHAFORGE_SIGNED_EXECUTION_SEMANTICS,
            "requires_alphaforge_runtime": True,
            "signalforge_import_required_by_alphaforge": False,
        },
        "symbols": [symbol],
        "datetime_range": {
            "start": start_date,
            "end": end_date,
        },
    }


def _build_manifest(
    *,
    package_name: str,
    package_version: str,
    package_label: str,
    symbol: str,
    start_date: str,
    end_date: str,
    row_count: int,
) -> dict[str, Any]:
    return {
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
        "row_count": row_count,
        "schema_version": SIGNAL_CONTRACT_V02,
        "alpha_forge_strategy": ALPHAFORGE_CUSTOM_SIGNAL_STRATEGY,
        "expected_alpha_forge_execution_semantics": ALPHAFORGE_SIGNED_EXECUTION_SEMANTICS,
        "contains_backtest_results": False,
        "contains_performance_metrics": False,
    }


def _build_readme(
    *,
    package_label: str,
    start_date: str,
    end_date: str,
    development_end: str,
    holdout_start: str,
    signal_name: str,
    source: str,
    factor_name: str,
) -> str:
    return f"""# AlphaForge v0.2 Compatibility Smoke Package

This package is a deterministic SignalForge v0.2 smoke export for AlphaForge `custom_signal` validation.

SignalForge generated the signal artifacts in this package.
AlphaForge should validate and backtest the package contents.
AlphaForge must not import SignalForge internals.

## Package

- Package: `{package_label}`
- Signal: `{signal_name}`
- Source: `{source}`
- Factor: `{factor_name}`
- Signal contract: `{SIGNAL_CONTRACT_V02}`
- AlphaForge strategy: `{ALPHAFORGE_CUSTOM_SIGNAL_STRATEGY}`
- Expected execution semantics: `{ALPHAFORGE_SIGNED_EXECUTION_SEMANTICS}`

## Files

- `market_data.csv`
- `signal.csv`
- `signal_contract.yaml`
- `data_quality_report.json`
- `manifest.json`
- `README.md`

## AlphaForge Validation

Use the package with AlphaForge's custom signal workflow and signed runtime:

```bash
python3 -m alphaforge.cli research-validate \
  --strategy custom_signal \
  --data market_data.csv \
  --signal-file signal.csv \
  --execution-semantics signed_close_to_close_lagged
```

## Split Dates

- Development: {start_date} to {development_end}
- Holdout: {holdout_start} to {end_date}

Both splits contain at least one row in this package.
"""


def _single_unique_value(df: pd.DataFrame, column: str) -> Any:
    unique_values = df[column].dropna().unique()
    if len(unique_values) != 1:
        raise ExportError(f"Expected exactly one unique value for {column}, got {len(unique_values)}")
    return unique_values[0]


def _sorted_unique_dates(series: pd.Series) -> list[pd.Timestamp]:
    dates = pd.Index(normalize_declared_daily_trading_date(series).unique())
    return list(dates.sort_values())


def _write_csv(df: pd.DataFrame, path: Path) -> Path:
    df.to_csv(path, index=False, lineterminator="\n")
    return path


def _write_yaml(data: dict[str, Any], path: Path) -> Path:
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False)
    return path


def _write_json(data: dict[str, Any], path: Path) -> Path:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write("\n")
    return path


def _write_text(text: str, path: Path) -> Path:
    with open(path, "w", encoding="utf-8") as f:
        f.write(text if text.endswith("\n") else text + "\n")
    return path
