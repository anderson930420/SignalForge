"""Conversion from factor output to signal artifact rows."""

import pandas as pd

from signalforge.schemas import SIGNAL_COLUMNS


SIGNAL_BINARY_RULE = "signal_binary = 1 if signal_value > 0 else 0"


class SignalComposer:
    """Compose signal artifacts from factor outputs.

    MVP rule for signal_binary derivation:
        signal_binary = 1 if signal_value > 0 else 0

    This rule is applied when signal_binary is not explicitly provided
    by the factor output.

    Accepts either:
    - Canonical factor output (datetime, symbol, factor_name, factor_value, available_at)
    - Legacy factor output (just factor_value/signal_value column)
    """

    def __init__(self) -> None:
        self.validator = None

    def set_validator(self, validator) -> None:
        """Set the signal validator."""
        self.validator = validator

    def compose(
        self,
        factor_output: pd.DataFrame,
        datetime: pd.Timestamp | pd.Series | list | tuple | None = None,
        available_at: pd.Timestamp | pd.Series | list | tuple | None = None,
        symbol: str | None = None,
        signal_name: str | None = None,
        source: str | None = None,
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

        Returns:
            DataFrame conforming to signal artifact schema

        Raises:
            SignalValidationError: If composed signal fails validation
        """
        result = _compose_signal_frame(
            factor_output=factor_output,
            datetime=datetime,
            available_at=available_at,
            symbol=symbol,
            signal_name=signal_name,
            source=source,
        )

        if self.validator is not None:
            self.validator.validate_or_raise(result)

        return result


def compose_signal(
    factor_output: pd.DataFrame,
    datetime: pd.Timestamp | pd.Series | list | tuple | None = None,
    available_at: pd.Timestamp | pd.Series | list | tuple | None = None,
    symbol: str | None = None,
    signal_name: str | None = None,
    source: str | None = None,
) -> pd.DataFrame:
    """Convert factor output to signal artifact rows.

    MVP rule: signal_binary = 1 if signal_value > 0 else 0

    Args:
        factor_output: DataFrame from factor calculation with canonical columns
        datetime: Timestamp for the signal (optional if factor_output has datetime)
        available_at: When signal became available (optional if factor_output has available_at)
        symbol: Ticker symbol (optional if factor_output has symbol)
        signal_name: Name of the signal/factor (optional if factor_output has factor_name)
        source: Source identifier

    Returns:
        DataFrame conforming to signal artifact schema
    """
    return _compose_signal_frame(
        factor_output=factor_output,
        datetime=datetime,
        available_at=available_at,
        symbol=symbol,
        signal_name=signal_name,
        source=source,
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
) -> pd.DataFrame:
    if len(factor_output) == 0:
        return pd.DataFrame(columns=SIGNAL_COLUMNS)

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

    result = pd.DataFrame(index=range(n_rows))
    result["datetime"] = _as_series(dt_values, n_rows)
    result["available_at"] = _as_series(av_values, n_rows)
    result["symbol"] = sym_value
    result["signal_name"] = sn_value
    result["source"] = source

    if "factor_value" in factor_output.columns:
        signal_values = factor_output["factor_value"].reset_index(drop=True)
    elif "signal_value" in factor_output.columns:
        signal_values = factor_output["signal_value"].reset_index(drop=True)
    else:
        signal_values = pd.Series([None] * n_rows)
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
