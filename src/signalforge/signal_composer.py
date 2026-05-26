"""Conversion from factor output to signal artifact rows."""

import pandas as pd

from signalforge.schemas import SIGNAL_COLUMNS
from signalforge.signal_semantics import (
    SIGNAL_CONTRACT_V02,
    V02_SIGNAL_COLUMNS,
    SignedUnitWeightPolicy,
    score_to_direction,
    score_to_target_weight,
    validate_v02_signal_frame,
)


SIGNAL_CONTRACT_V01 = "v0.1"
DEFAULT_SIGNAL_CONTRACT_VERSION = SIGNAL_CONTRACT_V01
SUPPORTED_SIGNAL_CONTRACT_VERSIONS = (SIGNAL_CONTRACT_V01, SIGNAL_CONTRACT_V02)
SIGNAL_BINARY_RULE = "signal_binary = 1 if signal_value > 0 else 0"


class SignalComposer:
    """Compose signal artifacts from factor outputs.

    Default behavior remains the legacy v0.1 long/flat signal contract:
        signal_binary = 1 if signal_value > 0 else 0

    v0.2 output is opt-in through ``contract_version=\"v0.2\"`` and emits
    score, direction, and target_weight. SignalForge still emits alpha
    semantics only; execution actions are derived downstream.

    Accepts either:
    - Canonical factor output (datetime, symbol, factor_name, factor_value, available_at)
    - Legacy factor output (just factor_value/signal_value column)
    """

    def __init__(self) -> None:
        self.validator = None

    def set_validator(self, validator) -> None:
        """Set the legacy v0.1 signal validator."""
        self.validator = validator

    def compose(
        self,
        factor_output: pd.DataFrame,
        datetime: pd.Timestamp | pd.Series | list | tuple | None = None,
        available_at: pd.Timestamp | pd.Series | list | tuple | None = None,
        symbol: str | None = None,
        signal_name: str | None = None,
        source: str | None = None,
        *,
        contract_version: str = DEFAULT_SIGNAL_CONTRACT_VERSION,
        weight_policy: SignedUnitWeightPolicy | None = None,
    ) -> pd.DataFrame:
        """Convert factor output to signal artifact rows.

        Args:
            factor_output: DataFrame from factor calculation with canonical columns:
                datetime, symbol, factor_name, factor_value, available_at
                OR legacy format with just factor_value/signal_value column
            datetime: Timestamp for the signal (optional if factor_output has datetime)
            available_at: When signal became available (optional if factor_output has available_at)
            symbol: Ticker symbol (optional if factor_output has symbol)
            signal_name: Name of the signal/factor (optional if factor_output has factor_name)
            source: Source identifier
            contract_version: ``v0.1`` for legacy signal_binary output or ``v0.2``
                for score/direction/target_weight output.
            weight_policy: Optional v0.2 score-to-target-weight policy.

        Returns:
            DataFrame conforming to the requested signal artifact schema

        Raises:
            SignalValidationError: If composed v0.1 signal fails validation
            ValueError: If composed v0.2 signal fails validation
        """
        result = _compose_signal_frame(
            factor_output=factor_output,
            datetime=datetime,
            available_at=available_at,
            symbol=symbol,
            signal_name=signal_name,
            source=source,
            contract_version=contract_version,
            weight_policy=weight_policy,
        )

        if self.validator is not None and contract_version == SIGNAL_CONTRACT_V01:
            self.validator.validate_or_raise(result)

        return result


def compose_signal(
    factor_output: pd.DataFrame,
    datetime: pd.Timestamp | pd.Series | list | tuple | None = None,
    available_at: pd.Timestamp | pd.Series | list | tuple | None = None,
    symbol: str | None = None,
    signal_name: str | None = None,
    source: str | None = None,
    *,
    contract_version: str = DEFAULT_SIGNAL_CONTRACT_VERSION,
    weight_policy: SignedUnitWeightPolicy | None = None,
) -> pd.DataFrame:
    """Convert factor output to signal artifact rows.

    Default behavior remains v0.1. Use ``contract_version=\"v0.2\"`` to emit
    score, direction, and target_weight.
    """
    return _compose_signal_frame(
        factor_output=factor_output,
        datetime=datetime,
        available_at=available_at,
        symbol=symbol,
        signal_name=signal_name,
        source=source,
        contract_version=contract_version,
        weight_policy=weight_policy,
    )


def _as_series(value, length: int) -> pd.Series:
    if isinstance(value, pd.Series):
        if len(value) != length:
            raise ValueError(f"Expected {length} values, got {len(value)}")
        return value.reset_index(drop=True)
    if isinstance(value, (pd.Index, list, tuple)):
        if len(value) != length:
            raise ValueError(f"Expected {length} values, got {len(value)}")
        return pd.Series(list(value))
    return pd.Series([value] * length)


def _compose_signal_frame(
    factor_output: pd.DataFrame,
    datetime: pd.Timestamp | pd.Series | list | tuple | None,
    available_at: pd.Timestamp | pd.Series | list | tuple | None,
    symbol: str | None,
    signal_name: str | None,
    source: str,
    *,
    contract_version: str,
    weight_policy: SignedUnitWeightPolicy | None,
) -> pd.DataFrame:
    if contract_version not in SUPPORTED_SIGNAL_CONTRACT_VERSIONS:
        raise ValueError(f"Unsupported signal contract version: {contract_version!r}")
    if contract_version == SIGNAL_CONTRACT_V02:
        return _compose_v02_signal_frame(
            factor_output=factor_output,
            datetime=datetime,
            available_at=available_at,
            symbol=symbol,
            signal_name=signal_name,
            source=source,
            weight_policy=weight_policy,
        )
    return _compose_v01_signal_frame(
        factor_output=factor_output,
        datetime=datetime,
        available_at=available_at,
        symbol=symbol,
        signal_name=signal_name,
        source=source,
    )


def _resolve_common_signal_fields(
    factor_output: pd.DataFrame,
    datetime: pd.Timestamp | pd.Series | list | tuple | None,
    available_at: pd.Timestamp | pd.Series | list | tuple | None,
    symbol: str | None,
    signal_name: str | None,
) -> tuple[pd.Series, pd.Series, str, str]:
    n_rows = len(factor_output)

    if "datetime" in factor_output.columns and datetime is None:
        dt_values = factor_output["datetime"]
    elif datetime is None:
        raise ValueError("datetime must be provided")
    else:
        dt_values = datetime

    if "available_at" in factor_output.columns and available_at is None:
        av_values = factor_output["available_at"]
    elif available_at is None:
        raise ValueError("available_at must be provided")
    else:
        av_values = available_at

    if "symbol" in factor_output.columns and symbol is None:
        sym_value = factor_output["symbol"].iloc[0]
    elif symbol is None:
        raise ValueError("symbol must be provided")
    else:
        sym_value = symbol

    if "factor_name" in factor_output.columns and signal_name is None:
        sn_value = factor_output["factor_name"].iloc[0]
    elif signal_name is None:
        raise ValueError("signal_name must be provided")
    else:
        sn_value = signal_name

    return _as_series(dt_values, n_rows), _as_series(av_values, n_rows), sym_value, sn_value


def _resolve_score_values(factor_output: pd.DataFrame, n_rows: int) -> pd.Series:
    if "factor_value" in factor_output.columns:
        return factor_output["factor_value"].reset_index(drop=True)
    if "signal_value" in factor_output.columns:
        return factor_output["signal_value"].reset_index(drop=True)
    if "score" in factor_output.columns:
        return factor_output["score"].reset_index(drop=True)
    return pd.Series([None] * n_rows)


def _compose_v01_signal_frame(
    factor_output: pd.DataFrame,
    datetime: pd.Timestamp | pd.Series | list | tuple | None,
    available_at: pd.Timestamp | pd.Series | list | tuple | None,
    symbol: str | None,
    signal_name: str | None,
    source: str,
) -> pd.DataFrame:
    if len(factor_output) == 0:
        return pd.DataFrame(columns=SIGNAL_COLUMNS)

    n_rows = len(factor_output)
    dt_values, av_values, sym_value, sn_value = _resolve_common_signal_fields(
        factor_output,
        datetime,
        available_at,
        symbol,
        signal_name,
    )

    result = pd.DataFrame(index=range(n_rows))
    result["datetime"] = dt_values
    result["available_at"] = av_values
    result["symbol"] = sym_value
    result["signal_name"] = sn_value
    result["source"] = source

    signal_values = _resolve_score_values(factor_output, n_rows)
    result["signal_value"] = signal_values

    if "signal_binary" in factor_output.columns:
        explicit_binary = factor_output["signal_binary"].reset_index(drop=True)
        result["signal_binary"] = explicit_binary.where(explicit_binary.notna(), 0)
    else:
        binary_values = []
        for value in result["signal_value"]:
            if pd.isna(value):
                binary_values.append(0)
            else:
                binary_values.append(1 if float(value) > 0 else 0)
        result["signal_binary"] = binary_values

    result = result[SIGNAL_COLUMNS]
    return result


def _compose_v02_signal_frame(
    factor_output: pd.DataFrame,
    datetime: pd.Timestamp | pd.Series | list | tuple | None,
    available_at: pd.Timestamp | pd.Series | list | tuple | None,
    symbol: str | None,
    signal_name: str | None,
    source: str,
    weight_policy: SignedUnitWeightPolicy | None,
) -> pd.DataFrame:
    if len(factor_output) == 0:
        return pd.DataFrame(columns=V02_SIGNAL_COLUMNS)

    n_rows = len(factor_output)
    policy = weight_policy or SignedUnitWeightPolicy()
    dt_values, av_values, sym_value, sn_value = _resolve_common_signal_fields(
        factor_output,
        datetime,
        available_at,
        symbol,
        signal_name,
    )
    score_values = pd.to_numeric(_resolve_score_values(factor_output, n_rows), errors="raise")

    result = pd.DataFrame(index=range(n_rows))
    result["datetime"] = dt_values
    result["available_at"] = av_values
    result["symbol"] = sym_value
    result["signal_name"] = sn_value
    result["score"] = score_values
    result["direction"] = [score_to_direction(value, neutral_threshold=policy.neutral_threshold) for value in score_values]
    result["target_weight"] = [score_to_target_weight(value, policy) for value in score_values]
    result["source"] = source

    return validate_v02_signal_frame(result.loc[:, list(V02_SIGNAL_COLUMNS)])
