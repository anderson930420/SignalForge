"""Tests for data_registry module."""

import pandas as pd
import pytest

from signalforge.data_registry import load_ohlcv_csv, validate_ohlcv_quality
from signalforge.schemas import MissingColumnsError


class TestLoadOhlcvCsv:
    def test_loads_valid_csv(self, tmp_path):
        csv_content = """datetime,open,high,low,close,volume
2024-01-01,100.0,105.0,99.0,102.0,1000000
2024-01-02,102.0,107.0,101.0,104.0,1100000
"""
        filepath = tmp_path / "test.csv"
        filepath.write_text(csv_content)

        df = load_ohlcv_csv(str(filepath))

        assert list(df.columns) == ["datetime", "open", "high", "low", "close", "volume"]
        assert len(df) == 2

    def test_raises_missing_columns_error(self, tmp_path):
        csv_content = """datetime,open,close
2024-01-01,100.0,102.0
"""
        filepath = tmp_path / "test.csv"
        filepath.write_text(csv_content)

        with pytest.raises(MissingColumnsError):
            load_ohlcv_csv(str(filepath))


class TestValidateOhlcvQuality:
    def test_detects_null_values(self):
        df = pd.DataFrame({
            "datetime": pd.date_range("2024-01-01", periods=3),
            "open": [100.0, None, 102.0],
            "high": [105.0, 106.0, 107.0],
            "low": [99.0, 100.0, 101.0],
            "close": [102.0, 103.0, 104.0],
            "volume": [1000000, 1100000, 1200000],
        })

        issues = validate_ohlcv_quality(df)

        assert any(i["code"] == "NULL_OHLCV" for i in issues)

    def test_detects_price_integrity_violations(self):
        df = pd.DataFrame({
            "datetime": pd.date_range("2024-01-01", periods=3),
            "open": [100.0, 102.0, 103.0],
            "high": [105.0, 95.0, 107.0],
            "low": [99.0, 100.0, 101.0],
            "close": [102.0, 103.0, 104.0],
            "volume": [1000000, 1100000, 1200000],
        })

        issues = validate_ohlcv_quality(df)

        assert any(i["code"] == "PRICE_INTEGRITY_VIOLATION" for i in issues)