from __future__ import annotations

import pandas as pd
import pytest

from signalforge.signal_semantics import (
    SIGNAL_CONTRACT_V02,
    V02_SIGNAL_COLUMNS,
    SignedUnitWeightPolicy,
    build_v02_signal_frame,
    score_to_direction,
    score_to_target_weight,
    validate_v02_signal_frame,
)


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


def test_v02_contract_constant_names_shared_signal_version() -> None:
    assert SIGNAL_CONTRACT_V02 == "v0.2"
    assert list(V02_SIGNAL_COLUMNS) == [
        "datetime",
        "available_at",
        "symbol",
        "signal_name",
        "score",
        "direction",
        "target_weight",
        "source",
    ]


@pytest.mark.parametrize(
    ("score", "expected"),
    [
        (2.0, 1),
        (0.0, 0),
        (-2.0, -1),
    ],
)
def test_score_to_direction_maps_signed_scores(score: float, expected: int) -> None:
    assert score_to_direction(score) == expected


def test_score_to_direction_respects_neutral_threshold() -> None:
    assert score_to_direction(0.1, neutral_threshold=0.2) == 0
    assert score_to_direction(0.3, neutral_threshold=0.2) == 1
    assert score_to_direction(-0.3, neutral_threshold=0.2) == -1


def test_score_to_target_weight_uses_signed_unit_policy() -> None:
    policy = SignedUnitWeightPolicy(max_abs_weight=0.5)

    assert score_to_target_weight(1.0, policy) == pytest.approx(0.5)
    assert score_to_target_weight(0.0, policy) == pytest.approx(0.0)
    assert score_to_target_weight(-1.0, policy) == pytest.approx(-0.5)


@pytest.mark.parametrize("max_abs_weight", [0.0, -0.1, 1.1])
def test_signed_unit_weight_policy_rejects_invalid_weight(max_abs_weight: float) -> None:
    with pytest.raises(ValueError):
        SignedUnitWeightPolicy(max_abs_weight=max_abs_weight)


def test_build_v02_signal_frame_maps_factor_value_to_score_direction_and_target_weight() -> None:
    signal = build_v02_signal_frame(
        _factor_output(),
        source="SignalForge",
    )

    assert signal.columns.tolist() == list(V02_SIGNAL_COLUMNS)
    assert signal["score"].tolist() == [1.5, 0.0, -2.0]
    assert signal["direction"].tolist() == [1, 0, -1]
    assert signal["target_weight"].tolist() == [1.0, 0.0, -1.0]
    assert signal["signal_name"].unique().tolist() == ["demo_factor"]
    assert signal["source"].unique().tolist() == ["SignalForge"]


def test_build_v02_signal_frame_accepts_explicit_signal_name_and_fractional_policy() -> None:
    signal = build_v02_signal_frame(
        _factor_output(),
        source="SignalForge",
        signal_name="demo_signal_v02",
        policy=SignedUnitWeightPolicy(max_abs_weight=0.25),
    )

    assert signal["signal_name"].unique().tolist() == ["demo_signal_v02"]
    assert signal["target_weight"].tolist() == [0.25, 0.0, -0.25]


def test_build_v02_signal_frame_rejects_missing_score_column() -> None:
    frame = _factor_output().drop(columns=["factor_value"])

    with pytest.raises(ValueError, match="Missing required factor output columns"):
        build_v02_signal_frame(frame, source="SignalForge")


def test_build_v02_signal_frame_rejects_missing_scores() -> None:
    frame = _factor_output()
    frame.loc[0, "factor_value"] = None

    with pytest.raises(ValueError, match="score contains missing values"):
        build_v02_signal_frame(frame, source="SignalForge")


def test_validate_v02_signal_frame_rejects_execution_action_columns() -> None:
    frame = build_v02_signal_frame(_factor_output(), source="SignalForge")
    frame["order_side"] = ["BUY", "NONE", "SELL"]

    with pytest.raises(ValueError, match="Column order mismatch"):
        validate_v02_signal_frame(frame)


def test_validate_v02_signal_frame_rejects_duplicate_signal_keys() -> None:
    frame = build_v02_signal_frame(_factor_output(), source="SignalForge")
    frame.loc[1, "datetime"] = frame.loc[0, "datetime"]

    with pytest.raises(ValueError, match="Duplicate datetime-symbol-signal_name"):
        validate_v02_signal_frame(frame)


def test_validate_v02_signal_frame_rejects_non_ternary_direction() -> None:
    frame = build_v02_signal_frame(_factor_output(), source="SignalForge")
    frame.loc[0, "direction"] = 2

    with pytest.raises(ValueError, match="direction must be ternary"):
        validate_v02_signal_frame(frame)
