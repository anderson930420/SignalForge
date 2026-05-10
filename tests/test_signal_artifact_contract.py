"""Tests for signal artifact contract."""

import pandas as pd
import pytest

from signalforge.schemas import SignalValidator, SignalValidationError
from signalforge.signal_composer import SignalComposer, compose_signal, SIGNAL_BINARY_RULE
from signalforge.export import export_signal_csv


class TestSignalValidator:
    """Tests for SignalValidator."""

    def test_validates_correct_schema(self):
        df = pd.DataFrame({
            "datetime": pd.date_range("2024-01-01", periods=3, tz="UTC"),
            "available_at": pd.date_range("2024-01-01", periods=3, tz="UTC"),
            "symbol": ["AAPL"] * 3,
            "signal_name": ["test"] * 3,
            "signal_value": [0.5, 0.6, 0.7],
            "signal_binary": [1, 1, 1],
            "source": ["test"] * 3,
        })

        validator = SignalValidator()
        errors = validator.validate(df)

        assert len(errors) == 0

    def test_detects_wrong_column_count(self):
        df = pd.DataFrame({
            "datetime": pd.date_range("2024-01-01", periods=3, tz="UTC"),
            "symbol": ["AAPL"] * 3,
        })

        validator = SignalValidator()
        errors = validator.validate(df)

        assert any("7 columns" in e for e in errors)

    def test_detects_column_order_mismatch(self):
        df = pd.DataFrame({
            "symbol": ["AAPL"] * 3,
            "datetime": pd.date_range("2024-01-01", periods=3, tz="UTC"),
            "available_at": pd.date_range("2024-01-01", periods=3, tz="UTC"),
            "signal_name": ["test"] * 3,
            "signal_value": [0.5, 0.6, 0.7],
            "signal_binary": [1, 1, 1],
            "source": ["test"] * 3,
        })

        validator = SignalValidator()
        errors = validator.validate(df)

        assert any("Column order mismatch" in e for e in errors)

    def test_detects_invalid_binary_values(self):
        df = pd.DataFrame({
            "datetime": pd.date_range("2024-01-01", periods=3, tz="UTC"),
            "available_at": pd.date_range("2024-01-01", periods=3, tz="UTC"),
            "symbol": ["AAPL"] * 3,
            "signal_name": ["test"] * 3,
            "signal_value": [0.5, 0.6, 0.7],
            "signal_binary": [0, 2, 1],
            "source": ["test"] * 3,
        })

        validator = SignalValidator()
        errors = validator.validate(df)

        assert any("signal_binary" in e and "0 or 1" in e for e in errors)

    def test_detects_available_at_greater_than_datetime(self):
        df = pd.DataFrame({
            "datetime": pd.date_range("2024-01-01", periods=3, tz="UTC"),
            "available_at": pd.date_range("2024-01-02", periods=3, tz="UTC"),
            "symbol": ["AAPL"] * 3,
            "signal_name": ["test"] * 3,
            "signal_value": [0.5, 0.6, 0.7],
            "signal_binary": [1, 1, 1],
            "source": ["test"] * 3,
        })

        validator = SignalValidator()
        errors = validator.validate(df)

        assert any("available_at > datetime" in e for e in errors)

    def test_detects_null_in_required_columns(self):
        df = pd.DataFrame({
            "datetime": pd.date_range("2024-01-01", periods=3, tz="UTC"),
            "available_at": pd.date_range("2024-01-01", periods=3, tz="UTC"),
            "symbol": [None, "AAPL", "AAPL"],
            "signal_name": ["test"] * 3,
            "signal_value": [0.5, 0.6, 0.7],
            "signal_binary": [1, 1, 1],
            "source": ["test"] * 3,
        })

        validator = SignalValidator()
        errors = validator.validate(df)

        assert any("Null values found in required column: symbol" in e for e in errors)

    def test_detects_duplicate_datetime_symbol_signal_name(self):
        df = pd.DataFrame({
            "datetime": [pd.Timestamp("2024-01-01", tz="UTC")] * 3,
            "available_at": [pd.Timestamp("2024-01-01", tz="UTC")] * 3,
            "symbol": ["AAPL", "AAPL", "AAPL"],
            "signal_name": ["test", "test", "test"],
            "signal_value": [0.5, 0.6, 0.7],
            "signal_binary": [1, 1, 1],
            "source": ["test"] * 3,
        })

        validator = SignalValidator()
        errors = validator.validate(df)

        assert any("Duplicate datetime-symbol-signal_name rows found" in e for e in errors)

    def test_validate_or_raise_raises_on_error(self):
        df = pd.DataFrame({
            "datetime": pd.date_range("2024-01-01", periods=3, tz="UTC"),
            "available_at": pd.date_range("2024-01-02", periods=3, tz="UTC"),
            "symbol": ["AAPL"] * 3,
            "signal_name": ["test"] * 3,
            "signal_value": [0.5, 0.6, 0.7],
            "signal_binary": [1, 1, 1],
            "source": ["test"] * 3,
        })

        validator = SignalValidator()

        with pytest.raises(SignalValidationError):
            validator.validate_or_raise(df)

    def test_validate_or_raise_passes_on_valid(self):
        df = pd.DataFrame({
            "datetime": pd.date_range("2024-01-01", periods=3, tz="UTC"),
            "available_at": pd.date_range("2024-01-01", periods=3, tz="UTC"),
            "symbol": ["AAPL", "GOOG", "MSFT"],
            "signal_name": ["test1", "test2", "test3"],
            "signal_value": [0.5, 0.6, 0.7],
            "signal_binary": [1, 1, 1],
            "source": ["test"] * 3,
        })

        validator = SignalValidator()
        validator.validate_or_raise(df)


class TestSignalBinaryRule:
    """Tests for MVP signal_binary derivation rule."""

    def test_rule_is_defined(self):
        assert SIGNAL_BINARY_RULE == "signal_binary = 1 if signal_value > 0 else 0"

    def test_positive_signal_value_gives_binary_1(self):
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

    def test_negative_signal_value_gives_binary_0(self):
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

    def test_zero_signal_value_gives_binary_0(self):
        factor_output = pd.DataFrame({"signal_value": [0.0]})
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


class TestSignalComposer:
    """Tests for SignalComposer class."""

    def test_compose_with_validation(self):
        factor_output = pd.DataFrame({"signal_value": [0.5]})
        datetime = pd.Timestamp("2024-01-01", tz="UTC")
        available_at = pd.Timestamp("2024-01-01", tz="UTC")

        composer = SignalComposer()
        composer.set_validator(SignalValidator())

        result = composer.compose(
            factor_output=factor_output,
            datetime=datetime,
            available_at=available_at,
            symbol="AAPL",
            signal_name="test_signal",
            source="test_source",
        )

        assert list(result.columns) == [
            "datetime", "available_at", "symbol", "signal_name",
            "signal_value", "signal_binary", "source"
        ]
        assert result["signal_binary"].iloc[0] == 1

    def test_compose_raises_on_invalid_signal(self):
        factor_output = pd.DataFrame({"signal_value": [0.5]})
        datetime = pd.Timestamp("2024-01-01", tz="UTC")
        available_at = pd.Timestamp("2024-01-02", tz="UTC")

        composer = SignalComposer()
        composer.set_validator(SignalValidator())

        with pytest.raises(SignalValidationError):
            composer.compose(
                factor_output=factor_output,
                datetime=datetime,
                available_at=available_at,
                symbol="AAPL",
                signal_name="test_signal",
                source="test_source",
            )

    def test_compose_full_series_preserves_warmup_rows(self):
        factor_output = pd.DataFrame({"signal_value": [None, 0.5, -0.25]})
        datetime = pd.date_range("2024-01-01", periods=3, tz="UTC")
        available_at = pd.date_range("2024-01-01", periods=3, tz="UTC")

        composer = SignalComposer()
        composer.set_validator(SignalValidator())

        result = composer.compose(
            factor_output=factor_output,
            datetime=datetime,
            available_at=available_at,
            symbol="AAPL",
            signal_name="test_signal",
            source="test_source",
        )

        assert len(result) == 3
        assert list(result.columns) == [
            "datetime", "available_at", "symbol", "signal_name",
            "signal_value", "signal_binary", "source"
        ]
        assert pd.isna(result["signal_value"].iloc[0])
        assert result["signal_binary"].tolist() == [0, 1, 0]
        assert (result["available_at"] <= result["datetime"]).all()


class TestDeterministicExport:
    """Tests for deterministic export."""

    def test_export_produces_identical_output(self, tmp_path):
        df = pd.DataFrame({
            "datetime": pd.date_range("2024-01-01", periods=10, tz="UTC"),
            "available_at": pd.date_range("2024-01-01", periods=10, tz="UTC"),
            "symbol": ["AAPL"] * 10,
            "signal_name": ["moskowitz_momentum"] * 10,
            "signal_value": [0.1 * i for i in range(10)],
            "signal_binary": [1] * 10,
            "source": ["moskowitz_2024"] * 10,
        })

        filepath1 = export_signal_csv(df, tmp_path / "run1", validate=False)
        filepath2 = export_signal_csv(df, tmp_path / "run2", validate=False)

        with open(filepath1) as f1:
            content1 = f1.read()
        with open(filepath2) as f2:
            content2 = f2.read()

        assert content1 == content2

    def test_export_stable_column_order(self, tmp_path):
        df = pd.DataFrame({
            "source": ["test"],
            "signal_binary": [1],
            "signal_value": [0.5],
            "signal_name": ["test"],
            "symbol": ["AAPL"],
            "available_at": pd.Timestamp("2024-01-01", tz="UTC"),
            "datetime": pd.Timestamp("2024-01-01", tz="UTC"),
        })

        filepath = export_signal_csv(df, tmp_path, validate=False)
        df_read = pd.read_csv(filepath)

        assert list(df_read.columns) == [
            "datetime", "available_at", "symbol", "signal_name",
            "signal_value", "signal_binary", "source"
        ]


class TestSignalArtifactContract:
    """Tests verifying all signal artifact contract requirements."""

    def test_required_columns_in_stable_order(self):
        expected = [
            "datetime",
            "available_at",
            "symbol",
            "signal_name",
            "signal_value",
            "signal_binary",
            "source",
        ]

        from signalforge.schemas import SIGNAL_COLUMNS
        assert SIGNAL_COLUMNS == expected

    def test_signal_binary_only_0_or_1(self):
        df = pd.DataFrame({
            "datetime": pd.date_range("2024-01-01", periods=3, tz="UTC"),
            "available_at": pd.date_range("2024-01-01", periods=3, tz="UTC"),
            "symbol": ["AAPL"] * 3,
            "signal_name": ["test"] * 3,
            "signal_value": [0.5, 0.6, 0.7],
            "signal_binary": [0, 1, 1],
            "source": ["test"] * 3,
        })

        validator = SignalValidator()
        errors = validator.validate(df)

        assert len(errors) == 0

    def test_available_at_less_than_or_equal_datetime(self):
        df = pd.DataFrame({
            "datetime": pd.date_range("2024-01-02", periods=3, tz="UTC"),
            "available_at": pd.date_range("2024-01-01", periods=3, tz="UTC"),
            "symbol": ["AAPL"] * 3,
            "signal_name": ["test"] * 3,
            "signal_value": [0.5, 0.6, 0.7],
            "signal_binary": [1, 1, 1],
            "source": ["test"] * 3,
        })

        validator = SignalValidator()
        errors = validator.validate(df)

        assert len(errors) == 0

    def test_no_duplicate_datetime_symbol_signal_name(self):
        df = pd.DataFrame({
            "datetime": pd.date_range("2024-01-01", periods=3, tz="UTC"),
            "available_at": pd.date_range("2024-01-01", periods=3, tz="UTC"),
            "symbol": ["AAPL", "GOOG", "MSFT"],
            "signal_name": ["sig_a", "sig_b", "sig_c"],
            "signal_value": [0.5, 0.6, 0.7],
            "signal_binary": [1, 1, 1],
            "source": ["test"] * 3,
        })

        validator = SignalValidator()
        errors = validator.validate(df)

        assert len(errors) == 0
