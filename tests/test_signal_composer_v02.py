from __future__ import annotations

import pandas as pd
import pytest

from signalforge.schemas import SIGNAL_COLUMNS, SignalValidator
from signalforge.signal_composer import (
    DEFAULT_SIGNAL_CONTRACT_VERSION,
    SIGNAL_CONTRACT_V01,
    SUPPORTED_SIGNAL_CONTRACT_VERSIONS,
    SignalComposer,
    compose_signal,
)
from signalforge.signal_semantics import SIGNAL_CONTRACT_V02, V02_SIGNAL_COLUMNS, SignedUnitWeightPolicy


def _factor_output() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "datetime": ["2025-01-02", "2025-01-03", "2025-01-04"],
            "available_at": ["2025-01-01", "2025-01-02", "2025-01-03"],
            "symbol": ["SFDEMO", "SFDEMO", "SFDEMO"],
            "factor_name": ["demo_factor", "demo_factor", "demo_factor"],
            "factor_value": [1.5, 0.0, -2.0],
        }
    )


def test_composer_default_contract_remains_v01() -> None:
    assert DEFAULT_SIGNAL_CONTRACT_VERSION == SIGNAL_CONTRACT_V01
    assert SIGNAL_CONTRACT_V01 in SUPPORTED_SIGNAL_CONTRACT_VERSIONS
    assert SIGNAL_CONTRACT_V02 in SUPPORTED_SIGNAL_CONTRACT_VERSIONS

    composer = SignalComposer()
    signal = composer.compose(_factor_output(), source="SignalForge")

    assert signal.columns.tolist() == SIGNAL_COLUMNS
    assert signal["signal_value"].tolist() == [1.5, 0.0, -2.0]
    assert signal["signal_binary"].tolist() == [1, 0, 0]


def test_composer_v02_outputs_score_direction_and_target_weight() -> None:
    composer = SignalComposer()

    signal = composer.compose(
        _factor_output(),
        source="SignalForge",
        contract_version=SIGNAL_CONTRACT_V02,
    )

    assert signal.columns.tolist() == list(V02_SIGNAL_COLUMNS)
    assert signal["score"].tolist() == [1.5, 0.0, -2.0]
    assert signal["direction"].tolist() == [1, 0, -1]
    assert signal["target_weight"].tolist() == [1.0, 0.0, -1.0]
    assert signal["signal_name"].unique().tolist() == ["demo_factor"]
    assert signal["source"].unique().tolist() == ["SignalForge"]


def test_compose_signal_function_supports_v02_output() -> None:
    signal = compose_signal(
        _factor_output(),
        source="SignalForge",
        contract_version=SIGNAL_CONTRACT_V02,
        weight_policy=SignedUnitWeightPolicy(max_abs_weight=0.25),
    )

    assert signal.columns.tolist() == list(V02_SIGNAL_COLUMNS)
    assert signal["target_weight"].tolist() == [0.25, 0.0, -0.25]


def test_composer_v02_accepts_score_column_when_factor_value_is_absent() -> None:
    frame = _factor_output().drop(columns=["factor_value"])
    frame["score"] = [0.2, -0.2, 0.0]

    signal = SignalComposer().compose(
        frame,
        source="SignalForge",
        contract_version=SIGNAL_CONTRACT_V02,
    )

    assert signal["score"].tolist() == [0.2, -0.2, 0.0]
    assert signal["direction"].tolist() == [1, -1, 0]


def test_composer_v02_uses_explicit_signal_name_and_symbol_arguments() -> None:
    frame = pd.DataFrame({"factor_value": [1.0, -1.0]})

    signal = SignalComposer().compose(
        frame,
        datetime=["2025-01-02", "2025-01-03"],
        available_at=["2025-01-01", "2025-01-02"],
        symbol="MANUAL",
        signal_name="manual_v02",
        source="SignalForge",
        contract_version=SIGNAL_CONTRACT_V02,
    )

    assert signal["symbol"].unique().tolist() == ["MANUAL"]
    assert signal["signal_name"].unique().tolist() == ["manual_v02"]
    assert signal["direction"].tolist() == [1, -1]


def test_composer_v02_skips_legacy_v01_validator() -> None:
    composer = SignalComposer()
    composer.set_validator(SignalValidator())

    signal = composer.compose(
        _factor_output(),
        source="SignalForge",
        contract_version=SIGNAL_CONTRACT_V02,
    )

    assert signal.columns.tolist() == list(V02_SIGNAL_COLUMNS)


def test_composer_rejects_unknown_contract_version() -> None:
    with pytest.raises(ValueError, match="Unsupported signal contract version"):
        SignalComposer().compose(_factor_output(), source="SignalForge", contract_version="v9")


def test_composer_v02_rejects_missing_score_values() -> None:
    frame = _factor_output()
    frame.loc[0, "factor_value"] = None

    with pytest.raises(ValueError, match="score"):
        SignalComposer().compose(frame, source="SignalForge", contract_version=SIGNAL_CONTRACT_V02)
