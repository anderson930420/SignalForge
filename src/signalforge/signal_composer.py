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
    """

    def __init__(self) -> None:
        self.validator = None

    def set_validator(self, validator) -> None:
        """Set the signal validator."""
        self.validator = validator

    def compose(
        self,
        factor_output: pd.DataFrame,
        datetime: pd.Timestamp,
        available_at: pd.Timestamp,
        symbol: str,
        signal_name: str,
        source: str,
    ) -> pd.DataFrame:
        """Convert factor output to signal artifact rows.

        Args:
            factor_output: DataFrame from factor calculation (must have 'signal_value')
            datetime: Timestamp for the signal
            available_at: When signal became available
            symbol: Ticker symbol
            signal_name: Name of the signal/factor
            source: Source identifier

        Returns:
            DataFrame conforming to signal artifact schema

        Raises:
            SignalValidationError: If composed signal fails validation
        """
        result = pd.DataFrame()
        result["datetime"] = [datetime]
        result["available_at"] = [available_at]
        result["symbol"] = [symbol]
        result["signal_name"] = [signal_name]
        result["source"] = [source]

        if "signal_value" in factor_output.columns:
            result["signal_value"] = factor_output["signal_value"].iloc[0]
        else:
            result["signal_value"] = None

        if "signal_binary" in factor_output.columns:
            result["signal_binary"] = factor_output["signal_binary"].iloc[0]
        else:
            if result["signal_value"].iloc[0] is not None:
                result["signal_binary"] = (
                    1 if result["signal_value"].iloc[0] > 0 else 0
                )
            else:
                result["signal_binary"] = None

        result = result[SIGNAL_COLUMNS]

        if self.validator is not None:
            self.validator.validate_or_raise(result)

        return result


def compose_signal(
    factor_output: pd.DataFrame,
    datetime: pd.Timestamp,
    available_at: pd.Timestamp,
    symbol: str,
    signal_name: str,
    source: str,
) -> pd.DataFrame:
    """Convert factor output to signal artifact rows.

    MVP rule: signal_binary = 1 if signal_value > 0 else 0

    Args:
        factor_output: DataFrame from factor calculation (must have 'signal_value')
        datetime: Timestamp for the signal
        available_at: When signal became available
        symbol: Ticker symbol
        signal_name: Name of the signal/factor
        source: Source identifier

    Returns:
        DataFrame conforming to signal artifact schema
    """
    result = pd.DataFrame()
    result["datetime"] = [datetime]
    result["available_at"] = [available_at]
    result["symbol"] = [symbol]
    result["signal_name"] = [signal_name]
    result["source"] = [source]

    if "signal_value" in factor_output.columns:
        result["signal_value"] = factor_output["signal_value"].iloc[0]
    else:
        result["signal_value"] = None

    if "signal_binary" in factor_output.columns:
        result["signal_binary"] = factor_output["signal_binary"].iloc[0]
    else:
        if result["signal_value"].iloc[0] is not None:
            result["signal_binary"] = (
                1 if result["signal_value"].iloc[0] > 0 else 0
            )
        else:
            result["signal_binary"] = None

    result = result[SIGNAL_COLUMNS]

    return result
