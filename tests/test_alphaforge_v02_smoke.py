from __future__ import annotations

import json

import pandas as pd
import pytest
import yaml

from signalforge.alphaforge_v02_smoke import (
    ALPHAFORGE_CUSTOM_SIGNAL_STRATEGY,
    ALPHAFORGE_CUSTOM_SIGNAL_VERSION,
    ALPHAFORGE_SIGNED_EXECUTION_SEMANTICS,
    V02_SMOKE_PACKAGE_FILES,
    build_demo_market_data,
    build_demo_v02_signal,
    export_alphaforge_v02_compatibility_package,
    export_demo_alphaforge_v02_compatibility_package,
)
from signalforge.compatibility import validate_signal_market_date_alignment
from signalforge.schemas import ExportError
from signalforge.signal_semantics import SIGNAL_CONTRACT_V02, V02_SIGNAL_COLUMNS, validate_v02_signal_frame


def test_demo_v02_signal_is_valid_and_aligned_with_market_data() -> None:
    market_data = build_demo_market_data()
    signal = build_demo_v02_signal()

    assert market_data["datetime"].tolist() == signal["datetime"].tolist()
    assert validate_signal_market_date_alignment(signal, market_data) == []
    assert validate_v02_signal_frame(signal).columns.tolist() == list(V02_SIGNAL_COLUMNS)
    assert signal["direction"].tolist() == [0, 1, -1, 0]
    assert signal["target_weight"].tolist() == [0.0, 1.0, -1.0, 0.0]


def test_export_demo_alphaforge_v02_package_writes_expected_files(tmp_path) -> None:
    paths = export_demo_alphaforge_v02_compatibility_package(tmp_path)

    assert set(paths) == set(V02_SMOKE_PACKAGE_FILES)
    for relative_path in V02_SMOKE_PACKAGE_FILES:
        assert (tmp_path / relative_path).exists()

    signal = pd.read_csv(tmp_path / "signal.csv")
    assert signal.columns.tolist() == list(V02_SIGNAL_COLUMNS)
    assert signal["target_weight"].tolist() == [0.0, 1.0, -1.0, 0.0]


def test_export_demo_alphaforge_v02_package_contract_marks_alphaforge_compatibility(tmp_path) -> None:
    export_demo_alphaforge_v02_compatibility_package(tmp_path)

    contract = yaml.safe_load((tmp_path / "signal_contract.yaml").read_text())

    assert contract["version"] == "0.2.0"
    assert contract["output"]["schema_version"] == SIGNAL_CONTRACT_V02
    assert contract["output"]["columns"] == list(V02_SIGNAL_COLUMNS)
    assert contract["compatibility"]["alphaforge_strategy"] == ALPHAFORGE_CUSTOM_SIGNAL_STRATEGY
    assert contract["compatibility"]["alphaforge_custom_signal_version"] == ALPHAFORGE_CUSTOM_SIGNAL_VERSION
    assert contract["compatibility"]["expected_execution_semantics"] == ALPHAFORGE_SIGNED_EXECUTION_SEMANTICS
    assert contract["compatibility"]["signalforge_import_required_by_alphaforge"] is False


def test_export_demo_alphaforge_v02_package_manifest_is_not_a_backtest_claim(tmp_path) -> None:
    export_demo_alphaforge_v02_compatibility_package(tmp_path)

    manifest = json.loads((tmp_path / "manifest.json").read_text())

    assert manifest["schema_version"] == SIGNAL_CONTRACT_V02
    assert manifest["alpha_forge_strategy"] == ALPHAFORGE_CUSTOM_SIGNAL_STRATEGY
    assert manifest["expected_alpha_forge_execution_semantics"] == ALPHAFORGE_SIGNED_EXECUTION_SEMANTICS
    assert manifest["contains_backtest_results"] is False
    assert manifest["contains_performance_metrics"] is False


def test_export_demo_alphaforge_v02_package_readme_documents_runtime_boundary(tmp_path) -> None:
    export_demo_alphaforge_v02_compatibility_package(tmp_path)

    readme = (tmp_path / "README.md").read_text()

    assert "AlphaForge must not import SignalForge internals" in readme
    assert "--strategy custom_signal" in readme
    assert "--execution-semantics signed_close_to_close_lagged" in readme


def test_export_alphaforge_v02_package_rejects_misaligned_dates(tmp_path) -> None:
    market_data = build_demo_market_data()
    signal = build_demo_v02_signal()
    signal.loc[0, "datetime"] = "2030-01-01"

    with pytest.raises(ExportError, match="date alignment"):
        export_alphaforge_v02_compatibility_package(market_data, signal, tmp_path)


def test_export_alphaforge_v02_package_rejects_out_of_bounds_target_weight(tmp_path) -> None:
    market_data = build_demo_market_data()
    signal = build_demo_v02_signal()
    signal.loc[1, "target_weight"] = 1.5

    with pytest.raises(ValueError, match="target_weight"):
        export_alphaforge_v02_compatibility_package(market_data, signal, tmp_path)
