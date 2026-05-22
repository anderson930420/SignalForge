"""Tests for the AlphaForge compatibility smoke package builder."""

from __future__ import annotations

import ast
import json
from pathlib import Path
import tomllib

import numpy as np
import pandas as pd
import yaml

from signalforge.export import export_alphaforge_compatibility_package
from signalforge.schemas import SIGNAL_COLUMNS


PACKAGE_NAME = "AAPL_20230101_20241231"
PACKAGE_DIRNAME = "alphaforge_compatibility"


def _build_market_data() -> pd.DataFrame:
    dates = pd.bdate_range("2023-01-03", "2024-12-31", tz="UTC")
    scale = np.linspace(0.0, 12.0, len(dates))
    cycle = np.sin(np.linspace(0.0, 18.0, len(dates)))
    close = 150.0 + scale + cycle
    open_ = np.r_[close[0], close[:-1]]
    high = np.maximum(open_, close) + 0.75
    low = np.minimum(open_, close) - 0.75
    volume = 1_000_000 + np.arange(len(dates)) * 10_000

    return pd.DataFrame(
        {
            "datetime": dates,
            "open": open_,
            "high": high,
            "low": low,
            "close": close,
            "volume": volume,
        }
    )


def _build_signal_data(market_data: pd.DataFrame) -> pd.DataFrame:
    signal_value = np.cos(np.linspace(0.0, 9.0, len(market_data)))
    signal_binary = (signal_value > 0).astype(int)

    return pd.DataFrame(
        {
            "datetime": market_data["datetime"],
            "available_at": market_data["datetime"],
            "symbol": "AAPL",
            "signal_name": "smoke_signal",
            "signal_value": signal_value,
            "signal_binary": signal_binary,
            "source": "smoke_source",
        }
    )


def test_exports_alphaforge_compatibility_package(tmp_path: Path) -> None:
    market_data = _build_market_data()
    signal_data = _build_signal_data(market_data)
    output_dir = tmp_path / PACKAGE_DIRNAME / PACKAGE_NAME

    paths = export_alphaforge_compatibility_package(
        market_data_df=market_data,
        signal_df=signal_data,
        output_dir=output_dir,
        signal_name="smoke_signal",
        source="smoke_source",
        factor_name="smoke_factor",
        factor_params={"lookback_days": 21, "skip_days": 1},
    )

    expected_files = {
        "market_data.csv",
        "signal.csv",
        "signal_contract.yaml",
        "data_quality_report.json",
        "manifest.json",
        "README.md",
    }

    assert output_dir.is_dir()
    assert set(paths) == expected_files
    assert {path.name for path in output_dir.iterdir()} == expected_files
    assert all(path.exists() for path in paths.values())

    market_csv = pd.read_csv(paths["market_data.csv"])
    signal_csv = pd.read_csv(paths["signal.csv"])

    assert list(market_csv.columns) == [
        "datetime",
        "open",
        "high",
        "low",
        "close",
        "volume",
    ]
    assert list(signal_csv.columns) == [
        "datetime",
        "available_at",
        "symbol",
        "signal_name",
        "signal_value",
        "signal_binary",
        "source",
    ]
    assert len(signal_csv) > 1

    for column in ["open", "high", "low", "close"]:
        values = market_csv[column]
        assert np.isfinite(values).all()
        assert (values > 0).all()
    assert (market_csv["high"] >= market_csv["low"]).all()
    assert (market_csv["high"] >= market_csv["open"]).all()
    assert (market_csv["high"] >= market_csv["close"]).all()
    assert (market_csv["low"] <= market_csv["open"]).all()
    assert (market_csv["low"] <= market_csv["close"]).all()
    assert not market_csv["volume"].isnull().any()

    signal_csv["datetime"] = pd.to_datetime(signal_csv["datetime"], utc=True)
    signal_csv["available_at"] = pd.to_datetime(signal_csv["available_at"], utc=True)
    market_csv["datetime"] = pd.to_datetime(market_csv["datetime"], utc=True)

    assert (signal_csv["available_at"] <= signal_csv["datetime"]).all()
    assert signal_csv["signal_binary"].isin([0, 1]).all()
    assert not signal_csv.duplicated(subset=["datetime", "symbol", "signal_name"]).any()
    assert set(signal_csv["datetime"]) == set(market_csv["datetime"])

    contract_data = yaml.safe_load(paths["signal_contract.yaml"].read_text(encoding="utf-8"))
    report_data = paths["data_quality_report.json"].read_text(encoding="utf-8")
    manifest_data = paths["manifest.json"].read_text(encoding="utf-8")
    readme_text = paths["README.md"].read_text(encoding="utf-8")

    report_json = json.loads(report_data)
    manifest_json = json.loads(manifest_data)

    assert set(contract_data) == {
        "signal_name",
        "version",
        "source",
        "factor",
        "decision_rule",
        "data",
        "timing",
        "output",
    }
    assert contract_data["signal_name"] == "smoke_signal"
    assert contract_data["source"] == "smoke_source"
    assert contract_data["factor"] == {
        "name": "smoke_factor",
        "version": "0.1.0",
        "parameters": {"lookback_days": 21, "skip_days": 1},
    }
    assert contract_data["decision_rule"] == {
        "signal_binary": "signal_binary = 1 if signal_value > 0 else 0",
    }
    assert contract_data["timing"] == {
        "available_at_rule": "same declared daily trading date as datetime for OHLCV-only daily signal",
    }
    assert contract_data["output"]["file"] == "signal.csv"
    assert contract_data["output"]["columns"] == SIGNAL_COLUMNS

    assert set(report_json) == {
        "version",
        "generator",
        "dataset_name",
        "source_type",
        "symbol_count",
        "row_count",
        "start_date",
        "end_date",
        "duplicate_rows",
        "missing_values",
        "warnings",
        "point_in_time_correctness_claimed",
    }
    assert report_json["row_count"] == len(signal_csv)
    assert report_json["missing_values"] == {
        "open": 0,
        "high": 0,
        "low": 0,
        "close": 0,
        "volume": 0,
    }
    assert report_json["point_in_time_correctness_claimed"] is False
    assert manifest_json["row_count"] == len(signal_csv)
    assert manifest_json["alpha_forge_strategy"] == "custom_signal"
    assert (
        manifest_json["expected_alpha_forge_execution_semantics"]
        == "legacy_close_to_close_lagged"
    )
    assert manifest_json["contains_backtest_results"] is False
    assert manifest_json["contains_performance_metrics"] is False

    assert "alphaforge research-validate --strategy custom_signal" in readme_text
    assert "market_data.csv" in readme_text
    assert "signal.csv" in readme_text
    assert "Development:" in readme_text
    assert "Holdout:" in readme_text

    dev_line = next(line for line in readme_text.splitlines() if line.startswith("- Development:"))
    holdout_line = next(line for line in readme_text.splitlines() if line.startswith("- Holdout:"))
    assert dev_line != holdout_line


def test_runtime_has_no_alphaforge_imports_or_dependency() -> None:
    project_root = Path(__file__).resolve().parents[1]

    for source_path in (project_root / "src" / "signalforge").rglob("*.py"):
        tree = ast.parse(source_path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                assert all(not alias.name.lower().startswith("alphaforge") for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module is not None:
                assert not node.module.lower().startswith("alphaforge")

    pyproject = tomllib.loads((project_root / "pyproject.toml").read_text(encoding="utf-8"))
    dependencies = pyproject["project"]["dependencies"]
    assert all("alphaforge" not in dependency.lower() for dependency in dependencies)
