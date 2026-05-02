"""Tests for signal_composer module."""

import pandas as pd

from signalforge.signal_composer import compose_signal


class TestComposeSignal:
    def test_produces_correct_columns(self):
        factor_output = pd.DataFrame({"signal_value": [0.5]})
        datetime = pd.Timestamp("2024-01-01", tz="UTC")
        available_at = pd.Timestamp("2024-01-01", tz="UTC")

        result = compose_signal(
            factor_output=factor_output,
            datetime=datetime,
            available_at=available_at,
            symbol="AAPL",
            signal_name="test_signal",
            source="test_source",
        )

        assert list(result.columns) == [
            "datetime",
            "available_at",
            "symbol",
            "signal_name",
            "signal_value",
            "signal_binary",
            "source",
        ]

    def test_derives_binary_from_positive_value(self):
        factor_output = pd.DataFrame({"signal_value": [0.5]})
        datetime = pd.Timestamp("2024-01-01", tz="UTC")
        available_at = pd.Timestamp("2024-01-01", tz="UTC")

        result = compose_signal(
            factor_output=factor_output,
            datetime=datetime,
            available_at=available_at,
            symbol="AAPL",
            signal_name="test_signal",
            source="test_source",
        )

        assert result["signal_binary"].iloc[0] == 1

    def test_derives_binary_from_negative_value(self):
        factor_output = pd.DataFrame({"signal_value": [-0.5]})
        datetime = pd.Timestamp("2024-01-01", tz="UTC")
        available_at = pd.Timestamp("2024-01-01", tz="UTC")

        result = compose_signal(
            factor_output=factor_output,
            datetime=datetime,
            available_at=available_at,
            symbol="AAPL",
            signal_name="test_signal",
            source="test_source",
        )

        assert result["signal_binary"].iloc[0] == 0

    def test_preserves_explicit_signal_binary(self):
        factor_output = pd.DataFrame({"signal_value": [0.5], "signal_binary": [0]})
        datetime = pd.Timestamp("2024-01-01", tz="UTC")
        available_at = pd.Timestamp("2024-01-01", tz="UTC")

        result = compose_signal(
            factor_output=factor_output,
            datetime=datetime,
            available_at=available_at,
            symbol="AAPL",
            signal_name="test_signal",
            source="test_source",
        )

        assert result["signal_binary"].iloc[0] == 0

    def test_preserves_null_signal_value(self):
        factor_output = pd.DataFrame({"signal_value": [None]})
        datetime = pd.Timestamp("2024-01-01", tz="UTC")
        available_at = pd.Timestamp("2024-01-01", tz="UTC")

        result = compose_signal(
            factor_output=factor_output,
            datetime=datetime,
            available_at=available_at,
            symbol="AAPL",
            signal_name="test_signal",
            source="test_source",
        )

        assert pd.isnull(result["signal_value"].iloc[0])