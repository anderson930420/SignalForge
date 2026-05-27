"""Package real SignalForge v0.2 artifacts for AlphaForge.

This module turns real `signalforge generate --config` output into the same
file-package boundary that AlphaForge's `smoke-signalforge-package` command
already consumes.

It intentionally does not import or execute AlphaForge.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from signalforge.alphaforge_v02_smoke import (
    V02_SMOKE_PACKAGE_FILES,
    export_alphaforge_v02_compatibility_package,
)
from signalforge.compatibility import normalize_declared_daily_trading_date
from signalforge.schemas import ExportError, OHLCV_COLUMNS
from signalforge.signal_semantics import SIGNAL_CONTRACT_V02, V02_SIGNAL_COLUMNS, validate_v02_signal_frame


GENERATED_V02_ARTIFACT_FILES = (
    "signal.csv",
    "signal_contract.yaml",
    "data_quality_report.json",
)


def export_alphaforge_v02_package_from_generated_artifacts(
    *,
    artifact_dir: Path,
    market_data_path: Path,
    output_dir: Path,
    package_name: str = "alphaforge_v02_generated_artifact_package",
    package_version: str = "1.0.0",
) -> dict[str, Path]:
    """Export an AlphaForge-compatible package from real generated artifacts."""
    artifact_dir = Path(artifact_dir)
    market_data_path = Path(market_data_path)
    output_dir = Path(output_dir)

    _validate_generated_artifact_dir(artifact_dir)
    if not market_data_path.exists():
        raise ExportError(f"market_data file does not exist: {market_data_path}")

    signal = validate_v02_signal_frame(pd.read_csv(artifact_dir / "signal.csv"))
    market_data = _load_and_align_market_data(market_data_path, signal)

    contract = _read_yaml(artifact_dir / "signal_contract.yaml")
    factor = contract.get("factor", {}) if isinstance(contract, dict) else {}
    factor_name = str(factor.get("name", "generated_signalforge_factor"))
    factor_version = str(factor.get("version", "unknown"))
    factor_params = factor.get("parameters", {})
    if not isinstance(factor_params, dict):
        factor_params = {}

    generated_for = f"{artifact_dir.parent.name}/{artifact_dir.name}" if artifact_dir.parent.name else artifact_dir.name

    return export_alphaforge_v02_compatibility_package(
        market_data,
        signal,
        output_dir,
        package_name=package_name,
        package_version=package_version,
        generated_for=generated_for,
        factor_name=factor_name,
        factor_version=factor_version,
        factor_params=factor_params,
    )


def package_output_files_exist(output_dir: Path) -> list[Path]:
    """Return existing AlphaForge package files in output_dir."""
    return [Path(output_dir) / filename for filename in V02_SMOKE_PACKAGE_FILES if (Path(output_dir) / filename).exists()]


def _validate_generated_artifact_dir(artifact_dir: Path) -> None:
    if not artifact_dir.exists() or not artifact_dir.is_dir():
        raise ExportError(f"artifact_dir does not exist or is not a directory: {artifact_dir}")

    missing = [name for name in GENERATED_V02_ARTIFACT_FILES if not (artifact_dir / name).exists()]
    if missing:
        raise ExportError(f"Missing generated SignalForge artifact files: {missing}")

    signal = pd.read_csv(artifact_dir / "signal.csv", nrows=5)
    if signal.columns.tolist() != list(V02_SIGNAL_COLUMNS):
        raise ExportError(
            "Generated signal.csv must use v0.2 columns: "
            f"expected {list(V02_SIGNAL_COLUMNS)}, got {signal.columns.tolist()}"
        )

    contract_text = (artifact_dir / "signal_contract.yaml").read_text(encoding="utf-8")
    required_fragments = (
        "schema_version: v0.2",
        "alphaforge_custom_signal_version: v0.2",
        "expected_execution_semantics: signed_close_to_close_lagged",
    )
    missing_fragments = [fragment for fragment in required_fragments if fragment not in contract_text]
    if missing_fragments:
        raise ExportError(f"signal_contract.yaml missing v0.2 compatibility fragments: {missing_fragments}")


def _load_and_align_market_data(market_data_path: Path, signal: pd.DataFrame) -> pd.DataFrame:
    market_data = pd.read_csv(market_data_path)
    market_data.columns = [str(column).lower().strip() for column in market_data.columns]

    if "date" in market_data.columns and "datetime" not in market_data.columns:
        market_data = market_data.rename(columns={"date": "datetime"})

    missing = [column for column in OHLCV_COLUMNS if column not in market_data.columns]
    if missing:
        raise ExportError(f"market_data missing required OHLCV columns: {missing}")

    market_data = market_data.loc[:, OHLCV_COLUMNS].copy()
    market_data["datetime"] = normalize_declared_daily_trading_date(market_data["datetime"])
    signal_dates = set(normalize_declared_daily_trading_date(signal["datetime"]))

    aligned = market_data[market_data["datetime"].isin(signal_dates)].copy()
    aligned_dates = set(aligned["datetime"])
    missing_dates = sorted(signal_dates - aligned_dates)
    if missing_dates:
        preview = [date.date().isoformat() for date in missing_dates[:5]]
        raise ExportError(f"market_data is missing dates required by signal.csv: {preview}")

    return aligned.sort_values("datetime").reset_index(drop=True)


def _read_yaml(path: Path) -> dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        parsed = yaml.safe_load(f)
    return parsed if isinstance(parsed, dict) else {}
