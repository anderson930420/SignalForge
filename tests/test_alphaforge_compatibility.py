"""Tests for alphaforge_compatibility module."""

import pandas as pd

from signalforge.compatibility import (
    validate_signal_csv,
    validate_signal_market_date_alignment,
    validate_signal_contract_yaml,
    validate_cross_artifacts,
)


class TestValidateSignalCsv:
    def test_validates_correct_schema(self):
        df = pd.DataFrame({
            "datetime": pd.date_range("2024-01-01", periods=3, tz="UTC"),
            "available_at": pd.date_range("2024-01-01", periods=3, tz="UTC"),
            "symbol": ["AAPL", "AAPL", "AAPL"],
            "signal_name": ["test", "test", "test"],
            "signal_value": [0.5, 0.6, 0.7],
            "signal_binary": [1, 1, 1],
            "source": ["test", "test", "test"],
        })

        errors = validate_signal_csv(df)

        assert len(errors) == 0

    def test_detects_wrong_column_count(self):
        df = pd.DataFrame({
            "datetime": pd.date_range("2024-01-01", periods=3, tz="UTC"),
            "symbol": ["AAPL", "AAPL", "AAPL"],
        })

        errors = validate_signal_csv(df)

        assert any("7 columns" in e for e in errors)

    def test_detects_invalid_binary_values(self):
        df = pd.DataFrame({
            "datetime": pd.date_range("2024-01-01", periods=3, tz="UTC"),
            "available_at": pd.date_range("2024-01-01", periods=3, tz="UTC"),
            "symbol": ["AAPL", "AAPL", "AAPL"],
            "signal_name": ["test", "test", "test"],
            "signal_value": [0.5, 0.6, 0.7],
            "signal_binary": [0, 2, 1],
            "source": ["test", "test", "test"],
        })

        errors = validate_signal_csv(df)

        assert any("signal_binary" in e and "0 or 1" in e for e in errors)

    def test_detects_available_at_greater_than_datetime(self):
        df = pd.DataFrame({
            "datetime": pd.date_range("2024-01-01", periods=3, tz="UTC"),
            "available_at": pd.date_range("2024-01-02", periods=3, tz="UTC"),
            "symbol": ["AAPL", "AAPL", "AAPL"],
            "signal_name": ["test", "test", "test"],
            "signal_value": [0.5, 0.6, 0.7],
            "signal_binary": [1, 1, 1],
            "source": ["test", "test", "test"],
        })

        errors = validate_signal_csv(df)

        assert any("available_at > datetime" in e for e in errors)


class TestValidateSignalContractYaml:
    def test_validates_correct_contract(self):
        data = {
            "signal_name": "test",
            "source": "test",
            "version": "0.1.0",
            "exported_at": "2024-01-01T00:00:00Z",
            "generator": "SignalForge",
            "compatibility": {
                "alphaforge_strategy": "custom_signal",
                "execution_semantics": "legacy_close_to_close_lagged",
                "target_position_rule": "target_position = float(signal_binary)",
                "supports_shorting": False,
                "supports_leverage": False,
            },
            "signals": [
                {
                    "signal_name": "test",
                    "source": "test",
                    "symbols": ["AAPL"],
                    "datetime_range": {
                        "start": "2024-01-01T00:00:00Z",
                        "end": "2024-01-02T00:00:00Z",
                    },
                    "row_count": 10,
                }
            ],
        }

        errors = validate_signal_contract_yaml(data)

        assert len(errors) == 0

    def test_detects_missing_required_keys(self):
        data = {}

        errors = validate_signal_contract_yaml(data)

        assert any("signal_name" in e for e in errors)
        assert any("generator" in e for e in errors)

    def test_detects_wrong_generator(self):
        data = {
            "signal_name": "test",
            "source": "test",
            "version": "0.1.0",
            "exported_at": "2024-01-01T00:00:00Z",
            "generator": "WrongGenerator",
            "compatibility": {
                "alphaforge_strategy": "custom_signal",
                "execution_semantics": "legacy_close_to_close_lagged",
                "target_position_rule": "target_position = float(signal_binary)",
                "supports_shorting": False,
                "supports_leverage": False,
            },
            "signals": [],
        }

        errors = validate_signal_contract_yaml(data)

        assert any("SignalForge" in e for e in errors)

    def test_detects_empty_signals_list(self):
        data = {
            "signal_name": "test",
            "source": "test",
            "version": "0.1.0",
            "exported_at": "2024-01-01T00:00:00Z",
            "generator": "SignalForge",
            "compatibility": {
                "alphaforge_strategy": "custom_signal",
                "execution_semantics": "legacy_close_to_close_lagged",
                "target_position_rule": "target_position = float(signal_binary)",
                "supports_shorting": False,
                "supports_leverage": False,
            },
            "signals": [],
        }

        errors = validate_signal_contract_yaml(data)

        assert any("non-empty" in e for e in errors)

    def test_detects_missing_signal_date_alignment(self):
        signal_df = pd.DataFrame({
            "datetime": pd.date_range("2024-01-02", periods=2, tz="UTC"),
            "available_at": pd.date_range("2024-01-02", periods=2, tz="UTC"),
            "symbol": ["AAPL", "AAPL"],
            "signal_name": ["test", "test"],
            "signal_value": [0.5, 0.6],
            "signal_binary": [1, 1],
            "source": ["test", "test"],
        })
        market_df = pd.DataFrame({
            "datetime": pd.date_range("2024-01-01", periods=2, tz="UTC"),
        })

        errors = validate_signal_market_date_alignment(signal_df, market_df)

        assert len(errors) > 0


class TestValidateCrossArtifacts:
    def test_detects_datetime_range_mismatch(self):
        df = pd.DataFrame({
            "datetime": pd.date_range("2024-01-01", "2024-01-10", periods=10, tz="UTC"),
            "available_at": pd.date_range("2024-01-01", "2024-01-10", periods=10, tz="UTC"),
            "symbol": ["AAPL"] * 10,
            "signal_name": ["test"] * 10,
            "signal_value": [0.5] * 10,
            "signal_binary": [1] * 10,
            "source": ["test"] * 10,
        })

        contract_data = {
            "version": "1.0",
            "exported_at": "2024-01-01T00:00:00Z",
            "generator": "SignalForge",
            "signals": [
                {
                    "signal_name": "test",
                    "source": "test",
                    "symbols": ["AAPL"],
                    "datetime_range": {
                        "start": "2024-01-15T00:00:00Z",
                        "end": "2024-01-20T00:00:00Z",
                    },
                    "row_count": 10,
                }
            ],
        }

        errors = validate_cross_artifacts(df, contract_data)

        assert len(errors) > 0
