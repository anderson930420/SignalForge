"""SignalForge producer-side signal semantics.

This module defines the v0.2 signal vocabulary shared with AlphaForge.

SignalForge is a signal producer. It should emit alpha semantics:
score, direction, and target_weight.

It should not emit execution actions such as Buy, Sell, Close Long,
Close Short, or Hold. Those actions are derived later by the execution
engine from current_weight -> target_weight.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

import pandas as pd


SIGNAL_CONTRACT_V02 = "v0.2"

V02_SIGNAL_COLUMNS = (
    "datetime",
    "available_at",
    "symbol",
    "signal_name",
    "score",
    "direction",
    "target_weight",
    "source",
)


@dataclass(frozen=True)
class SignedUnitWeightPolicy:
    """Map signed scores into no-leverage target weights."""

    max_abs_weight: float = 1.0
    neutral_threshold: float = 0.0

    def __post_init__(self) -> None:
        if self.max_abs_weight <= 0.0:
            raise ValueError("max_abs_weight must be positive")
        if self.max_abs_weight > 1.0:
            raise ValueError("max_abs_weight must be <= 1.0 under the no-leverage v0.2 contract")
        if self.neutral_threshold < 0.0:
            raise ValueError("neutral_threshold must be non-negative")


def score_to_direction(score: object, *, neutral_threshold: float = 0.0) -> int:
    """Map a numeric alpha score to ternary direction.

    Returns:
    - +1 for bullish scores
    - 0 for neutral scores
    - -1 for bearish scores
    """
    value = _coerce_score(score)
    if neutral_threshold < 0.0:
        raise ValueError("neutral_threshold must be non-negative")
    if value > neutral_threshold:
        return 1
    if value < -neutral_threshold:
        return -1
    return 0


def score_to_target_weight(score: object, policy: SignedUnitWeightPolicy | None = None) -> float:
    """Map a numeric alpha score to signed target exposure."""
    resolved_policy = policy or SignedUnitWeightPolicy()
    return float(score_to_direction(score, neutral_threshold=resolved_policy.neutral_threshold)) * float(
        resolved_policy.max_abs_weight
    )


def build_v02_signal_frame(
    factor_output: pd.DataFrame,
    *,
    score_column: str = "factor_value",
    datetime_column: str = "datetime",
    available_at_column: str = "available_at",
    symbol_column: str = "symbol",
    signal_name: str | None = None,
    source: str,
    policy: SignedUnitWeightPolicy | None = None,
) -> pd.DataFrame:
    """Build AlphaForge-compatible v0.2 signal rows from factor output.

    The output schema is intentionally the same as AlphaForge's v0.2
    `custom_signal` consumer contract.
    """
    resolved_policy = policy or SignedUnitWeightPolicy()
    _validate_required_columns(
        factor_output,
        [
            datetime_column,
            available_at_column,
            symbol_column,
            score_column,
        ],
    )

    result = pd.DataFrame(index=range(len(factor_output)))
    result["datetime"] = factor_output[datetime_column].reset_index(drop=True)
    result["available_at"] = factor_output[available_at_column].reset_index(drop=True)
    result["symbol"] = factor_output[symbol_column].astype(str).reset_index(drop=True)

    if signal_name is not None:
        result["signal_name"] = signal_name
    elif "factor_name" in factor_output.columns and len(factor_output) > 0:
        result["signal_name"] = factor_output["factor_name"].iloc[0]
    else:
        raise ValueError("signal_name must be provided when factor_output has no factor_name column")

    result["score"] = pd.to_numeric(factor_output[score_column], errors="raise").reset_index(drop=True)
    if result["score"].isna().any():
        raise ValueError("score contains missing values")

    result["direction"] = [
        score_to_direction(value, neutral_threshold=resolved_policy.neutral_threshold)
        for value in result["score"]
    ]
    result["target_weight"] = [
        score_to_target_weight(value, resolved_policy)
        for value in result["score"]
    ]
    result["source"] = source

    return validate_v02_signal_frame(result)


def validate_v02_signal_frame(frame: pd.DataFrame) -> pd.DataFrame:
    """Validate and return a canonical v0.2 signal frame."""
    errors: list[str] = []

    if tuple(frame.columns) != V02_SIGNAL_COLUMNS:
        errors.append(f"Column order mismatch: expected {list(V02_SIGNAL_COLUMNS)}, got {list(frame.columns)}")

    if "direction" in frame.columns and not frame["direction"].isin([-1, 0, 1]).all():
        errors.append("direction must be ternary: -1, 0, or 1")

    if "target_weight" in frame.columns:
        weights = pd.to_numeric(frame["target_weight"], errors="coerce")
        if weights.isna().any():
            errors.append("target_weight contains missing or non-numeric values")
        elif (weights < -1.0).any() or (weights > 1.0).any():
            errors.append("target_weight must be within [-1.0, 1.0]")

    required_non_null = [
        "datetime",
        "available_at",
        "symbol",
        "signal_name",
        "score",
        "direction",
        "target_weight",
        "source",
    ]
    for column in required_non_null:
        if column in frame.columns and frame[column].isna().any():
            errors.append(f"Null values found in required column: {column}")

    if {"available_at", "datetime"}.issubset(frame.columns):
        if (pd.to_datetime(frame["available_at"]) > pd.to_datetime(frame["datetime"])).any():
            errors.append("available_at must be less than or equal to datetime")

    duplicate_keys = ["datetime", "symbol", "signal_name"]
    if all(column in frame.columns for column in duplicate_keys):
        if frame.duplicated(subset=duplicate_keys, keep=False).any():
            errors.append("Duplicate datetime-symbol-signal_name rows found")

    if errors:
        raise ValueError("\n".join(errors))

    return frame.loc[:, list(V02_SIGNAL_COLUMNS)].copy()


def _validate_required_columns(frame: pd.DataFrame, columns: Iterable[str]) -> None:
    missing = [column for column in columns if column not in frame.columns]
    if missing:
        raise ValueError(f"Missing required factor output columns: {missing}")


def _coerce_score(score: object) -> float:
    if pd.isna(score):
        raise ValueError("score must not be missing")
    return float(score)
