from __future__ import annotations

import pandas as pd
import pytest

from signalforge.cli import (
    build_signed_unit_weight_policy,
    build_v02_signal_contract,
    export_generated_signal_csv,
    validate_config,
)
from signalforge.signal_semantics import SIGNAL_CONTRACT_V02, V02_SIGNAL_COLUMNS


def _valid_config() -> dict:
    return {
        "signal_name": "demo_signal",
        "source": "demo_source",
        "factor_name": "moskowitz_momentum",
        "data_source": {
            "type": "local_ohlcv_csv",
            "path": "/tmp/data.csv",
            "symbol": "DEMO",
        },
        "datetime_range": {
            "start": "2025-01-01",
            "end": "2025-01-31",
        },
        "output": {
            "artifacts_dir": "artifacts",
        },
    }


def test_validate_config_accepts_default_v01() -> None:
    assert validate_config(_valid_config()) == []


def test_validate_config_accepts_v02_signed_unit_config() -> None:
    config = _valid_config()
    config["signal_contract_version"] = "v0.2"
    config["target_weight"] = {
        "method": "signed_unit",
        "max_abs_weight": 0.5,
        "neutral_threshold": 0.1,
    }

    assert validate_config(config) == []


def test_validate_config_rejects_unknown_contract_version() -> None:
    config = _valid_config()
    config["signal_contract_version"] = "v9"

    errors = validate_config(config)

    assert any("signal_contract_version" in error for error in errors)


def test_validate_config_rejects_unknown_v02_target_weight_method() -> None:
    config = _valid_config()
    config["signal_contract_version"] = "v0.2"
    config["target_weight"] = {"method": "portfolio_optimizer"}

    errors = validate_config(config)

    assert any("target_weight.method" in error for error in errors)


def test_build_signed_unit_weight_policy_uses_v02_config() -> None:
    policy = build_signed_unit_weight_policy(
        {
            "target_weight": {
                "method": "signed_unit",
                "max_abs_weight": "0.25",
                "neutral_threshold": "0.1",
            }
        }
    )

    assert policy.max_abs_weight == pytest.approx(0.25)
    assert policy.neutral_threshold == pytest.approx(0.1)


def test_export_generated_signal_csv_writes_v02_columns(tmp_path) -> None:
    signal = pd.DataFrame(
        {
            "datetime": ["2025-01-02", "2025-01-01"],
            "available_at": ["2025-01-02", "2025-01-01"],
            "symbol": ["DEMO", "DEMO"],
            "signal_name": ["demo", "demo"],
            "score": [-1.0, 1.0],
            "direction": [-1, 1],
            "target_weight": [-1.0, 1.0],
            "source": ["test", "test"],
        }
    )

    output_path = export_generated_signal_csv(
        signal,
        tmp_path,
        signal_contract_version=SIGNAL_CONTRACT_V02,
    )

    exported = pd.read_csv(output_path)
    assert exported.columns.tolist() == list(V02_SIGNAL_COLUMNS)
    assert exported["datetime"].tolist() == ["2025-01-01", "2025-01-02"]


def test_build_v02_signal_contract_records_v02_schema_and_alphaforge_compatibility() -> None:
    contract = build_v02_signal_contract(
        signal_name="demo_signal",
        source="demo_source",
        factor_name="demo_factor",
        parameters={"lookback": 12},
        timing_rule="same declared daily trading date",
        symbols=["DEMO"],
        datetime_range=("2025-01-01", "2025-01-31"),
        factor_version="0.1.0",
        target_weight_config={"max_abs_weight": 0.5, "neutral_threshold": 0.1},
    )

    assert contract["version"] == "0.2.0"
    assert contract["output"]["schema_version"] == "v0.2"
    assert contract["output"]["columns"] == list(V02_SIGNAL_COLUMNS)
    assert contract["target_weight"] == {
        "method": "signed_unit",
        "max_abs_weight": 0.5,
        "neutral_threshold": 0.1,
    }
    assert contract["compatibility"]["alphaforge_custom_signal_version"] == "v0.2"
    assert contract["compatibility"]["expected_execution_semantics"] == "signed_close_to_close_lagged"
