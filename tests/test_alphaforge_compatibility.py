"""Tests for alphaforge_compatibility module."""

import pandas as pd
import pytest

from signalforge.compatibility import (
    normalize_declared_daily_trading_date,
    validate_signal_csv,
    validate_signal_market_date_alignment,
    validate_signal_contract_yaml,
    validate_cross_artifacts,
)


SIGNAL_COLUMNS = [
    "datetime",
    "available_at",
    "symbol",
    "signal_name",
    "signal_value",
    "signal_binary",
    "source",
]


def canonical_contract() -> dict:
    return {
        "signal_name": "test",
        "version": "0.1.0",
        "source": "test_source",
        "factor": {
            "name": "test_factor",
            "version": "0.1.0",
            "parameters": {"lookback_days": 252},
        },
        "decision_rule": {
            "signal_binary": "1 if signal_value > 0 else 0",
        },
        "data": {
            "required_columns": ["datetime", "open", "high", "low", "close", "volume", "symbol"],
        },
        "timing": {
            "available_at_rule": "same declared daily trading date as datetime for OHLCV-only daily signal",
        },
        "output": {
            "file": "signal.csv",
            "schema_version": "0.1.0",
            "columns": SIGNAL_COLUMNS,
        },
    }


def valid_signal_df() -> pd.DataFrame:
    return pd.DataFrame({
        "datetime": pd.date_range("2024-01-01", periods=3, tz="UTC"),
        "available_at": pd.date_range("2024-01-01", periods=3, tz="UTC"),
        "symbol": ["AAPL", "AAPL", "AAPL"],
        "signal_name": ["test", "test", "test"],
        "signal_value": [0.5, 0.6, 0.7],
        "signal_binary": [1, 1, 1],
        "source": ["test_source", "test_source", "test_source"],
    })


class TestValidateSignalCsv:
    def test_validates_correct_schema(self):
        df = valid_signal_df()

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

    def test_available_at_same_declared_date_passes_for_offset_timestamps(self):
        df = pd.DataFrame({
            "datetime": ["2025-01-02T00:00:00+08:00"],
            "available_at": ["2025-01-02 09:30:00+08:00"],
            "symbol": ["AAPL"],
            "signal_name": ["test"],
            "signal_value": [0.5],
            "signal_binary": [1],
            "source": ["test"],
        })

        errors = validate_signal_csv(df)

        assert errors == []

    def test_available_at_later_declared_date_fails_for_offset_timestamps(self):
        df = pd.DataFrame({
            "datetime": ["2025-01-02T23:30:00+08:00"],
            "available_at": ["2025-01-03T00:00:00+08:00"],
            "symbol": ["AAPL"],
            "signal_name": ["test"],
            "signal_value": [0.5],
            "signal_binary": [1],
            "source": ["test"],
        })

        errors = validate_signal_csv(df)

        assert any("available_at > datetime" in e for e in errors)

    def test_reports_unparseable_datetime_value(self):
        df = pd.DataFrame({
            "datetime": ["not-a-date"],
            "available_at": ["2025-01-02"],
            "symbol": ["AAPL"],
            "signal_name": ["test"],
            "signal_value": [0.5],
            "signal_binary": [1],
            "source": ["test"],
        })

        errors = validate_signal_csv(df)

        assert any("Invalid datetime or available_at value" in e for e in errors)


class TestDeclaredDailyTradingDateNormalization:
    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            ("2025-01-02", pd.Timestamp("2025-01-02")),
            ("2025-01-02T00:00:00Z", pd.Timestamp("2025-01-02")),
            ("2025-01-02T00:00:00+08:00", pd.Timestamp("2025-01-02")),
            ("2025-01-02 09:30:00+08:00", pd.Timestamp("2025-01-02")),
        ],
    )
    def test_preserves_declared_calendar_date(self, value, expected):
        assert normalize_declared_daily_trading_date(value) == expected

    def test_raises_clear_value_error_for_unparseable_value(self):
        with pytest.raises(ValueError, match="Invalid declared daily trading date"):
            normalize_declared_daily_trading_date("not-a-date")


class TestValidateSignalMarketDateAlignment:
    @pytest.mark.parametrize(
        "signal_datetime",
        [
            "2025-01-02T00:00:00+08:00",
            "2025-01-02T00:00:00Z",
            "2025-01-02 09:30:00+08:00",
        ],
    )
    def test_accepts_matching_declared_dates_for_offset_timestamps(self, signal_datetime):
        signal_df = pd.DataFrame({"datetime": [signal_datetime]})
        market_df = pd.DataFrame({"datetime": ["2025-01-02"]})

        errors = validate_signal_market_date_alignment(signal_df, market_df)

        assert errors == []

    def test_fails_when_declared_dates_differ(self):
        signal_df = pd.DataFrame({"datetime": ["2025-01-03T00:00:00+08:00"]})
        market_df = pd.DataFrame({"datetime": ["2025-01-02"]})

        errors = validate_signal_market_date_alignment(signal_df, market_df)

        assert any("signal dates must exactly match" in e for e in errors)

    def test_reports_unparseable_datetime_value(self):
        signal_df = pd.DataFrame({"datetime": ["not-a-date"]})
        market_df = pd.DataFrame({"datetime": ["2025-01-02"]})

        errors = validate_signal_market_date_alignment(signal_df, market_df)

        assert any("Invalid datetime value for date alignment" in e for e in errors)


class TestValidateSignalContractYaml:
    def test_validates_canonical_contract(self):
        data = canonical_contract()

        errors = validate_signal_contract_yaml(data)

        assert len(errors) == 0

    def test_detects_missing_required_keys(self):
        data = {}

        errors = validate_signal_contract_yaml(data)

        assert any("signal_name" in e for e in errors)
        assert any("factor" in e for e in errors)

    def test_detects_missing_factor_version(self):
        data = canonical_contract()
        del data["factor"]["version"]

        errors = validate_signal_contract_yaml(data)

        assert any("factor" in e and "version" in e for e in errors)

    def test_detects_missing_decision_rule_signal_binary(self):
        data = canonical_contract()
        data["decision_rule"] = {}

        errors = validate_signal_contract_yaml(data)

        assert any("decision_rule" in e and "signal_binary" in e for e in errors)

    def test_detects_wrong_output_columns(self):
        data = canonical_contract()
        data["output"]["columns"] = SIGNAL_COLUMNS[:-1]

        errors = validate_signal_contract_yaml(data)

        assert any("output.columns" in e for e in errors)

    def test_legacy_exported_at_is_not_required(self):
        data = canonical_contract()
        assert "exported_at" not in data
        assert "generator" not in data
        assert "signals" not in data

        errors = validate_signal_contract_yaml(data)

        assert len(errors) == 0

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
    def test_validates_matching_canonical_artifacts(self):
        errors = validate_cross_artifacts(valid_signal_df(), canonical_contract())

        assert len(errors) == 0

    def test_detects_column_mismatch(self):
        df = valid_signal_df().drop(columns=["source"])

        errors = validate_cross_artifacts(df, canonical_contract())

        assert any("columns" in e for e in errors)

    def test_detects_signal_name_mismatch(self):
        df = valid_signal_df()
        df.loc[0, "signal_name"] = "other"

        errors = validate_cross_artifacts(df, canonical_contract())

        assert any("signal_name" in e for e in errors)

    def test_detects_source_mismatch(self):
        df = valid_signal_df()
        df.loc[0, "source"] = "other_source"

        errors = validate_cross_artifacts(df, canonical_contract())

        assert any("source" in e for e in errors)
