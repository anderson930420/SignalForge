"""Tests for Moskowitz Momentum Factor."""

import pandas as pd
import pytest

from signalforge.factor_base import BaseAlphaFactor, FACTOR_OUTPUT_COLUMNS
from signalforge.factors.moskowitz_momentum import MoskowitzMomentumFactor


class TestMoskowitzMomentumFactor:
    def test_implements_base_alpha_factor(self):
        factor = MoskowitzMomentumFactor()
        assert isinstance(factor, BaseAlphaFactor)

    def test_has_name(self):
        factor = MoskowitzMomentumFactor()
        assert factor.name == "moskowitz_momentum"

    def test_has_version(self):
        factor = MoskowitzMomentumFactor()
        assert factor.version == "0.1.0"

    def test_required_inputs_returns_tuple(self):
        factor = MoskowitzMomentumFactor()
        required = factor.required_inputs()
        assert isinstance(required, tuple)
        assert required == ("datetime", "close", "symbol")

    def test_compute_returns_canonical_columns(self):
        data = pd.DataFrame({
            "datetime": pd.date_range("2024-01-01", periods=300, freq="D"),
            "open": [100.0] * 300,
            "high": [105.0] * 300,
            "low": [95.0] * 300,
            "close": [102.0 + i * 0.1 for i in range(300)],
            "volume": [1000000] * 300,
            "symbol": ["AAPL"] * 300,
        })

        factor = MoskowitzMomentumFactor()
        result = factor.compute(data)

        assert list(result.columns) == FACTOR_OUTPUT_COLUMNS
        assert "datetime" in result.columns
        assert "symbol" in result.columns
        assert "factor_name" in result.columns
        assert "factor_value" in result.columns
        assert "available_at" in result.columns

    def test_compute_output_has_factor_name(self):
        data = pd.DataFrame({
            "datetime": pd.date_range("2024-01-01", periods=300, freq="D"),
            "open": [100.0] * 300,
            "high": [105.0] * 300,
            "low": [95.0] * 300,
            "close": [102.0 + i * 0.1 for i in range(300)],
            "volume": [1000000] * 300,
            "symbol": ["AAPL"] * 300,
        })

        factor = MoskowitzMomentumFactor()
        result = factor.compute(data)

        assert result["factor_name"].iloc[0] == "moskowitz_momentum"

    def test_compute_output_has_available_at(self):
        data = pd.DataFrame({
            "datetime": pd.date_range("2024-01-01", periods=300, freq="D"),
            "open": [100.0] * 300,
            "high": [105.0] * 300,
            "low": [95.0] * 300,
            "close": [102.0 + i * 0.1 for i in range(300)],
            "volume": [1000000] * 300,
            "symbol": ["AAPL"] * 300,
        })

        factor = MoskowitzMomentumFactor()
        result = factor.compute(data)

        assert "available_at" in result.columns
        assert len(result["available_at"]) == len(result)

    def test_compute_does_not_contain_target_position(self):
        data = pd.DataFrame({
            "datetime": pd.date_range("2024-01-01", periods=300, freq="D"),
            "open": [100.0] * 300,
            "high": [105.0] * 300,
            "low": [95.0] * 300,
            "close": [102.0 + i * 0.1 for i in range(300)],
            "volume": [1000000] * 300,
            "symbol": ["AAPL"] * 300,
        })

        factor = MoskowitzMomentumFactor()
        result = factor.compute(data)

        assert "target_position" not in result.columns

    def test_compute_does_not_contain_signal_binary(self):
        data = pd.DataFrame({
            "datetime": pd.date_range("2024-01-01", periods=300, freq="D"),
            "open": [100.0] * 300,
            "high": [105.0] * 300,
            "low": [95.0] * 300,
            "close": [102.0 + i * 0.1 for i in range(300)],
            "volume": [1000000] * 300,
            "symbol": ["AAPL"] * 300,
        })

        factor = MoskowitzMomentumFactor()
        result = factor.compute(data)

        assert "signal_binary" not in result.columns

    def test_compute_formula(self):
        data = pd.DataFrame({
            "datetime": pd.date_range("2024-01-01", periods=300, freq="D"),
            "open": [100.0] * 300,
            "high": [105.0] * 300,
            "low": [95.0] * 300,
            "close": [100.0] * 300,
            "volume": [1000000] * 300,
            "symbol": ["AAPL"] * 300,
        })
        data.loc[200, "close"] = 110.0

        factor = MoskowitzMomentumFactor()
        result = factor.compute(data)

        valid_rows = result[result["factor_value"].notna()]
        assert len(valid_rows) > 0

    def test_legacy_calculate_still_works(self):
        data = pd.DataFrame({
            "datetime": pd.date_range("2024-01-01", periods=300, freq="D"),
            "open": [100.0] * 300,
            "high": [105.0] * 300,
            "low": [95.0] * 300,
            "close": [102.0 + i * 0.1 for i in range(300)],
            "volume": [1000000] * 300,
            "symbol": ["AAPL"] * 300,
        })

        factor = MoskowitzMomentumFactor()
        result = factor.calculate(data)

        assert "factor_value" in result.columns
        assert len(result) == len(data)

    def test_compute_missing_close_column(self):
        data = pd.DataFrame({
            "datetime": pd.date_range("2024-01-01", periods=10, freq="D"),
            "open": [100.0] * 10,
            "high": [105.0] * 10,
            "low": [95.0] * 10,
            "volume": [1000000] * 10,
            "symbol": ["AAPL"] * 10,
        })

        factor = MoskowitzMomentumFactor()

        with pytest.raises(ValueError, match="moskowitz_momentum.*close"):
            factor.compute(data)

    def test_compute_missing_datetime_column(self):
        data = pd.DataFrame({
            "open": [100.0] * 10,
            "high": [105.0] * 10,
            "low": [95.0] * 10,
            "close": [102.0] * 10,
            "volume": [1000000] * 10,
            "symbol": ["AAPL"] * 10,
        })

        factor = MoskowitzMomentumFactor()

        with pytest.raises(ValueError, match="moskowitz_momentum.*datetime"):
            factor.compute(data)

    def test_compute_missing_symbol_column(self):
        data = pd.DataFrame({
            "datetime": pd.date_range("2024-01-01", periods=10, freq="D"),
            "open": [100.0] * 10,
            "high": [105.0] * 10,
            "low": [95.0] * 10,
            "close": [102.0] * 10,
            "volume": [1000000] * 10,
        })

        factor = MoskowitzMomentumFactor()

        with pytest.raises(ValueError, match="moskowitz_momentum.*symbol"):
            factor.compute(data)
