from __future__ import annotations

import json

import pandas as pd
import yaml
from typer.testing import CliRunner

from signalforge.alphaforge_v02_smoke import V02_SMOKE_PACKAGE_FILES
from signalforge.alphaforge_v02_package import export_alphaforge_v02_package_from_generated_artifacts
from signalforge.cli import app
from signalforge.signal_semantics import V02_SIGNAL_COLUMNS


def _write_generated_artifacts(tmp_path):
    artifact_dir = tmp_path / "artifacts" / "2330.TW" / "tw_2330_moskowitz_v02" / "20200101_20250101"
    artifact_dir.mkdir(parents=True)

    pd.DataFrame(
        {
            "datetime": ["2021-01-04", "2021-01-05", "2021-01-06"],
            "available_at": ["2021-01-04", "2021-01-05", "2021-01-06"],
            "symbol": ["2330.TW", "2330.TW", "2330.TW"],
            "signal_name": ["tw_2330_moskowitz_v02", "tw_2330_moskowitz_v02", "tw_2330_moskowitz_v02"],
            "score": [0.2, -0.1, 0.0],
            "direction": [1, -1, 0],
            "target_weight": [1.0, -1.0, 0.0],
            "source": ["yfinance_2330_tw", "yfinance_2330_tw", "yfinance_2330_tw"],
        }
    ).to_csv(artifact_dir / "signal.csv", index=False)

    (artifact_dir / "signal_contract.yaml").write_text(
        """signal_name: tw_2330_moskowitz_v02
version: 0.2.0
source: yfinance_2330_tw
factor:
  name: moskowitz_momentum
  version: 0.1.0
  parameters: {}
output:
  file: signal.csv
  schema_version: v0.2
  columns:
  - datetime
  - available_at
  - symbol
  - signal_name
  - score
  - direction
  - target_weight
  - source
compatibility:
  alphaforge_strategy: custom_signal
  alphaforge_custom_signal_version: v0.2
  expected_execution_semantics: signed_close_to_close_lagged
""",
        encoding="utf-8",
    )
    (artifact_dir / "data_quality_report.json").write_text('{"dataset_name":"market_data.csv"}\n', encoding="utf-8")

    market_data = tmp_path / "data" / "2330_ohlcv.csv"
    market_data.parent.mkdir(parents=True)
    pd.DataFrame(
        {
            "datetime": ["2020-01-01", "2021-01-04", "2021-01-05", "2021-01-06"],
            "open": [100.0, 101.0, 102.0, 103.0],
            "high": [101.0, 102.0, 103.0, 104.0],
            "low": [99.0, 100.0, 101.0, 102.0],
            "close": [100.5, 101.5, 102.5, 103.5],
            "volume": [1000, 1100, 1200, 1300],
        }
    ).to_csv(market_data, index=False)

    return artifact_dir, market_data


def test_export_alphaforge_v02_package_from_generated_artifacts(tmp_path) -> None:
    artifact_dir, market_data = _write_generated_artifacts(tmp_path)
    output_dir = tmp_path / "package"

    paths = export_alphaforge_v02_package_from_generated_artifacts(
        artifact_dir=artifact_dir,
        market_data_path=market_data,
        output_dir=output_dir,
    )

    assert set(paths) == set(V02_SMOKE_PACKAGE_FILES)
    for filename in V02_SMOKE_PACKAGE_FILES:
        assert (output_dir / filename).exists()

    signal = pd.read_csv(output_dir / "signal.csv")
    assert signal.columns.tolist() == list(V02_SIGNAL_COLUMNS)
    assert signal["target_weight"].tolist() == [1.0, -1.0, 0.0]

    packaged_market_data = pd.read_csv(output_dir / "market_data.csv")
    assert packaged_market_data["datetime"].tolist() == ["2021-01-04", "2021-01-05", "2021-01-06"]

    manifest = json.loads((output_dir / "manifest.json").read_text())
    assert manifest["generator"] == "SignalForge"
    assert manifest["schema_version"] == "v0.2"
    assert manifest["contains_backtest_results"] is False
    assert manifest["contains_performance_metrics"] is False

    contract = yaml.safe_load((output_dir / "signal_contract.yaml").read_text())
    assert contract["output"]["schema_version"] == "v0.2"
    assert contract["compatibility"]["alphaforge_strategy"] == "custom_signal"


def test_package_alphaforge_v02_cli_writes_package(tmp_path) -> None:
    artifact_dir, market_data = _write_generated_artifacts(tmp_path)
    output_dir = tmp_path / "package"

    result = CliRunner().invoke(
        app,
        [
            "package-alphaforge-v02",
            "--artifact-dir",
            str(artifact_dir),
            "--market-data",
            str(market_data),
            "--output-dir",
            str(output_dir),
        ],
    )

    assert result.exit_code == 0, result.output
    summary = json.loads(result.output)
    assert summary["status"] == "packaged"
    assert summary["files"] == sorted(V02_SMOKE_PACKAGE_FILES)
    assert "smoke-signalforge-package" in summary["alpha_forge_command"]
    assert (output_dir / "manifest.json").exists()


def test_package_alphaforge_v02_cli_refuses_existing_package_without_overwrite(tmp_path) -> None:
    artifact_dir, market_data = _write_generated_artifacts(tmp_path)
    output_dir = tmp_path / "package"
    runner = CliRunner()

    first = runner.invoke(
        app,
        [
            "package-alphaforge-v02",
            "--artifact-dir",
            str(artifact_dir),
            "--market-data",
            str(market_data),
            "--output-dir",
            str(output_dir),
        ],
    )
    assert first.exit_code == 0, first.output

    second = runner.invoke(
        app,
        [
            "package-alphaforge-v02",
            "--artifact-dir",
            str(artifact_dir),
            "--market-data",
            str(market_data),
            "--output-dir",
            str(output_dir),
        ],
    )

    assert second.exit_code == 1
    assert "Output package files already exist" in second.output
