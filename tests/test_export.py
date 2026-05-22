"""Tests for export module."""

import json

import pandas as pd
import yaml

from signalforge.export import (
    export_signal_csv,
    export_signal_contract_yaml,
    export_data_quality_report,
    build_market_data_quality_report,
    build_signal_contract,
)


class TestExportSignalCsv:
    def test_exports_csv_with_correct_columns(self, tmp_path):
        df = pd.DataFrame({
            "datetime": [pd.Timestamp("2024-01-01", tz="UTC")],
            "available_at": [pd.Timestamp("2024-01-01", tz="UTC")],
            "symbol": ["AAPL"],
            "signal_name": ["test_signal"],
            "signal_value": [0.5],
            "signal_binary": [1],
            "source": ["test"],
        })

        filepath = export_signal_csv(df, tmp_path)

        assert filepath.name == "signal.csv"
        assert filepath.exists()

        df_read = pd.read_csv(filepath)
        assert list(df_read.columns) == [
            "datetime",
            "available_at",
            "symbol",
            "signal_name",
            "signal_value",
            "signal_binary",
            "source",
        ]


class TestExportSignalContractYaml:
    def test_exports_yaml(self, tmp_path):
        contract_data = {
            "version": "1.0",
            "exported_at": "2024-01-01T00:00:00Z",
            "generator": "SignalForge",
            "signals": [
                {
                    "signal_name": "test_signal",
                    "source": "test",
                    "symbols": ["AAPL"],
                    "datetime_range": {
                        "start": "2024-01-01T00:00:00Z",
                        "end": "2024-01-02T00:00:00Z",
                    },
                    "row_count": 1,
                    "signal_value_stats": {
                        "min": 0.5,
                        "max": 0.5,
                        "mean": 0.5,
                        "null_count": 0,
                    },
                    "signal_binary_stats": {
                        "value_0_count": 0,
                        "value_1_count": 1,
                        "null_count": 0,
                    },
                }
            ],
        }

        filepath = export_signal_contract_yaml(contract_data, tmp_path)

        assert filepath.name == "signal_contract.yaml"
        assert filepath.exists()

        with open(filepath) as f:
            loaded = yaml.safe_load(f)

        assert loaded["generator"] == "SignalForge"


class TestDeterministicExport:
    """Tests for deterministic artifact exports."""

    def test_signal_csv_sorted_deterministically(self, tmp_path):
        df1 = pd.DataFrame({
            "datetime": pd.to_datetime(["2024-01-01", "2024-01-03", "2024-01-02"]),
            "available_at": pd.to_datetime(["2024-01-01", "2024-01-03", "2024-01-02"]),
            "symbol": ["AAPL", "AAPL", "AAPL"],
            "signal_name": ["moskowitz_momentum", "moskowitz_momentum", "moskowitz_momentum"],
            "signal_value": [0.5, 0.3, 0.4],
            "signal_binary": [1, 1, 1],
            "source": ["test", "test", "test"],
        })
        df2 = df1.copy()

        export_signal_csv(df1, tmp_path, validate=False)
        export_signal_csv(df2, tmp_path, validate=False)

        with open(tmp_path / "signal.csv") as f:
            content1 = f.read()

        with open(tmp_path / "signal.csv") as f:
            content2 = f.read()

        assert content1 == content2
        lines = content1.strip().split("\n")
        assert lines[1].startswith("2024-01-01")
        assert lines[2].startswith("2024-01-02")
        assert lines[3].startswith("2024-01-03")

    def test_signal_contract_no_volatile_timestamps(self):
        contract = build_signal_contract(
            signal_name="moskowitz_momentum",
            source="moskowitz_2024",
            factor_name="moskowitz_momentum",
            parameters={"lookback_days": 252},
            decision_rule="1 if signal_value > 0 else 0",
            timing_rule="same declared daily trading date as datetime for OHLCV-only daily signal",
            symbols=["AAPL"],
            datetime_range=("2024-01-01", "2024-12-31"),
            row_count=100,
            signal_value_stats={"min": 0.1, "max": 0.5, "mean": 0.3, "null_count": 10},
            signal_binary_stats={"value_0_count": 30, "value_1_count": 70, "null_count": 0},
            symbol="AAPL",
            factor_version="0.1.0",
        )

        assert "exported_at" not in contract
        assert "generated_at" not in contract
        assert "created_at" not in contract
        assert "generator" not in contract

    def test_signal_contract_parameters_sorted(self):
        contract1 = build_signal_contract(
            signal_name="moskowitz_momentum",
            source="moskowitz_2024",
            factor_name="moskowitz_momentum",
            parameters={"z": 3, "a": 1, "m": 2},
            decision_rule="1 if signal_value > 0 else 0",
            timing_rule="same declared daily trading date as datetime for OHLCV-only daily signal",
            symbols=["AAPL"],
            datetime_range=("2024-01-01", "2024-12-31"),
            row_count=100,
            signal_value_stats={"min": 0.1, "max": 0.5, "mean": 0.3, "null_count": 10},
            signal_binary_stats={"value_0_count": 30, "value_1_count": 70, "null_count": 0},
            symbol="AAPL",
            factor_version="0.1.0",
        )
        contract2 = build_signal_contract(
            signal_name="moskowitz_momentum",
            source="moskowitz_2024",
            factor_name="moskowitz_momentum",
            parameters={"a": 1, "m": 2, "z": 3},
            decision_rule="1 if signal_value > 0 else 0",
            timing_rule="same declared daily trading date as datetime for OHLCV-only daily signal",
            symbols=["AAPL"],
            datetime_range=("2024-01-01", "2024-12-31"),
            row_count=100,
            signal_value_stats={"min": 0.1, "max": 0.5, "mean": 0.3, "null_count": 10},
            signal_binary_stats={"value_0_count": 30, "value_1_count": 70, "null_count": 0},
            symbol="AAPL",
            factor_version="0.1.0",
        )

        assert contract1["factor"]["parameters"] == contract2["factor"]["parameters"]
        assert list(contract1["factor"]["parameters"].keys()) == ["a", "m", "z"]

    def test_full_pipeline_deterministic(self, tmp_path):
        import numpy as np

        from signalforge.export import (
            export_signal_csv,
            export_signal_contract_yaml,
            export_data_quality_report,
            build_signal_contract,
            build_market_data_quality_report,
        )

        market_data = pd.DataFrame({
            "datetime": pd.date_range("2024-01-01", periods=100, freq="D"),
            "open": [100.0] * 100,
            "high": [105.0] * 100,
            "low": [95.0] * 100,
            "close": [102.0] * 100,
            "volume": [1000000] * 100,
            "symbol": ["AAPL"] * 100,
        })

        signal_df = pd.DataFrame({
            "datetime": pd.date_range("2024-01-01", periods=100, freq="D"),
            "available_at": pd.date_range("2024-01-01", periods=100, freq="D"),
            "symbol": ["AAPL"] * 100,
            "signal_name": ["moskowitz_momentum"] * 100,
            "signal_value": np.random.randn(100).tolist(),
            "signal_binary": [1 if v > 0 else 0 for v in np.random.randn(100)],
            "source": ["moskowitz_2024"] * 100,
        })

        contract1 = build_signal_contract(
            signal_name="moskowitz_momentum",
            source="moskowitz_2024",
            factor_name="moskowitz_momentum",
            parameters={"lookback_days": 252},
            decision_rule="1 if signal_value > 0 else 0",
            timing_rule="same declared daily trading date as datetime for OHLCV-only daily signal",
            symbols=["AAPL"],
            datetime_range=("2024-01-01", "2024-12-31"),
            row_count=len(signal_df),
            signal_value_stats={"min": 0.1, "max": 0.5, "mean": 0.3, "null_count": 10},
            signal_binary_stats={"value_0_count": 30, "value_1_count": 70, "null_count": 0},
            symbol="AAPL",
            factor_version="0.1.0",
        )
        market_report1 = build_market_data_quality_report(
            market_data=market_data,
            dataset_name="test.csv",
        )

        contract2 = build_signal_contract(
            signal_name="moskowitz_momentum",
            source="moskowitz_2024",
            factor_name="moskowitz_momentum",
            parameters={"lookback_days": 252},
            decision_rule="1 if signal_value > 0 else 0",
            timing_rule="same declared daily trading date as datetime for OHLCV-only daily signal",
            symbols=["AAPL"],
            datetime_range=("2024-01-01", "2024-12-31"),
            row_count=len(signal_df),
            signal_value_stats={"min": 0.1, "max": 0.5, "mean": 0.3, "null_count": 10},
            signal_binary_stats={"value_0_count": 30, "value_1_count": 70, "null_count": 0},
            symbol="AAPL",
            factor_version="0.1.0",
        )
        market_report2 = build_market_data_quality_report(
            market_data=market_data,
            dataset_name="test.csv",
        )

        assert contract1 == contract2
        assert market_report1 == market_report2

        output_dir1 = tmp_path / "run1"
        output_dir1.mkdir(parents=True, exist_ok=True)
        export_signal_csv(signal_df, output_dir1, validate=False)
        export_signal_contract_yaml(contract1, output_dir1)
        export_data_quality_report(market_report1, output_dir1)

        output_dir2 = tmp_path / "run2"
        output_dir2.mkdir(parents=True, exist_ok=True)
        export_signal_csv(signal_df, output_dir2, validate=False)
        export_signal_contract_yaml(contract2, output_dir2)
        export_data_quality_report(market_report2, output_dir2)

        with open(output_dir1 / "signal.csv") as f:
            csv1 = f.read()
        with open(output_dir2 / "signal.csv") as f:
            csv2 = f.read()
        assert csv1 == csv2

        with open(output_dir1 / "signal_contract.yaml") as f:
            contract_yaml1 = f.read()
        with open(output_dir2 / "signal_contract.yaml") as f:
            contract_yaml2 = f.read()
        assert contract_yaml1 == contract_yaml2

        with open(output_dir1 / "data_quality_report.json") as f:
            report1 = f.read()
        with open(output_dir2 / "data_quality_report.json") as f:
            report2 = f.read()
        assert report1 == report2

class TestBuildMarketDataQualityReport:
    def test_builds_report_from_ohlcv_data(self):
        market_data = pd.DataFrame({
            "datetime": pd.date_range("2024-01-01", periods=100, freq="D"),
            "open": [100.0] * 100,
            "high": [105.0] * 100,
            "low": [95.0] * 100,
            "close": [102.0] * 100,
            "volume": [1000000] * 100,
            "symbol": ["AAPL"] * 100,
        })

        report = build_market_data_quality_report(
            market_data=market_data,
            dataset_name="test_data.csv",
            source_type="local_ohlcv_csv",
        )

        assert report["dataset_name"] == "test_data.csv"
        assert report["source_type"] == "local_ohlcv_csv"
        assert report["symbol_count"] == 1
        assert report["row_count"] == 100
        assert report["start_date"] is not None
        assert report["end_date"] is not None
        assert report["duplicate_rows"] == 0
        assert isinstance(report["missing_values"], dict)
        assert "open" in report["missing_values"]
        assert "high" in report["missing_values"]
        assert "low" in report["missing_values"]
        assert "close" in report["missing_values"]
        assert "volume" in report["missing_values"]
        assert report["point_in_time_correctness_claimed"] is False

    def test_missing_values_is_per_column_dict(self):
        market_data = pd.DataFrame({
            "datetime": pd.date_range("2024-01-01", periods=10, freq="D"),
            "open": [100.0, None, 102.0, 103.0, 104.0, 105.0, 106.0, 107.0, 108.0, 109.0],
            "high": [105.0] * 10,
            "low": [95.0] * 10,
            "close": [102.0] * 10,
            "volume": [1000000] * 10,
            "symbol": ["AAPL"] * 10,
        })

        report = build_market_data_quality_report(
            market_data=market_data,
            dataset_name="test.csv",
        )

        assert report["missing_values"]["open"] == 1
        assert report["missing_values"]["high"] == 0
        assert report["missing_values"]["low"] == 0
        assert report["missing_values"]["close"] == 0
        assert report["missing_values"]["volume"] == 0

    def test_duplicate_rows_counted(self):
        market_data = pd.DataFrame({
            "datetime": pd.date_range("2024-01-01", periods=5, freq="D"),
            "open": [100.0] * 5,
            "high": [105.0] * 5,
            "low": [95.0] * 5,
            "close": [102.0] * 5,
            "volume": [1000000] * 5,
            "symbol": ["AAPL", "AAPL", "AAPL", "AAPL", "AAPL"],
        })
        market_data.loc[2, "datetime"] = market_data.loc[0, "datetime"]

        report = build_market_data_quality_report(
            market_data=market_data,
            dataset_name="test.csv",
        )

        assert report["duplicate_rows"] > 0

    def test_warnings_include_null_ohlcv(self):
        market_data = pd.DataFrame({
            "datetime": pd.date_range("2024-01-01", periods=10, freq="D"),
            "open": [100.0] * 10,
            "high": [105.0] * 10,
            "low": [95.0] * 10,
            "close": [None] * 10,
            "volume": [1000000] * 10,
            "symbol": ["AAPL"] * 10,
        })

        report = build_market_data_quality_report(
            market_data=market_data,
            dataset_name="test.csv",
        )

        warning_codes = [w["code"] for w in report["warnings"]]
        assert "NULL_CLOSE" in warning_codes

    def test_warnings_include_high_low_violations(self):
        market_data = pd.DataFrame({
            "datetime": pd.date_range("2024-01-01", periods=10, freq="D"),
            "open": [100.0] * 10,
            "high": [90.0] * 10,
            "low": [95.0] * 10,
            "close": [102.0] * 10,
            "volume": [1000000] * 10,
            "symbol": ["AAPL"] * 10,
        })

        report = build_market_data_quality_report(
            market_data=market_data,
            dataset_name="test.csv",
        )

        warning_codes = [w["code"] for w in report["warnings"]]
        assert "PRICE_INTEGRITY_VIOLATION" in warning_codes

    def test_point_in_time_correctness_false(self):
        market_data = pd.DataFrame({
            "datetime": pd.date_range("2024-01-01", periods=100, freq="D"),
            "open": [100.0] * 100,
            "high": [105.0] * 100,
            "low": [95.0] * 100,
            "close": [102.0] * 100,
            "volume": [1000000] * 100,
            "symbol": ["AAPL"] * 100,
        })

        report = build_market_data_quality_report(
            market_data=market_data,
            dataset_name="test.csv",
        )

        assert report["point_in_time_correctness_claimed"] is False

    def test_no_volatile_timestamps_in_market_report(self):
        market_data = pd.DataFrame({
            "datetime": pd.date_range("2024-01-01", periods=100, freq="D"),
            "open": [100.0] * 100,
            "high": [105.0] * 100,
            "low": [95.0] * 100,
            "close": [102.0] * 100,
            "volume": [1000000] * 100,
            "symbol": ["AAPL"] * 100,
        })

        report = build_market_data_quality_report(
            market_data=market_data,
            dataset_name="test.csv",
        )

        assert "exported_at" not in report
        assert "generated_at" not in report
        assert "created_at" not in report

    def test_warnings_sorted_deterministically(self):
        market_data = pd.DataFrame({
            "datetime": pd.date_range("2024-01-01", periods=10, freq="D"),
            "open": [None] * 10,
            "high": [90.0] * 10,
            "low": [95.0] * 10,
            "close": [102.0] * 10,
            "volume": [1000000] * 10,
            "symbol": ["AAPL"] * 10,
        })

        report1 = build_market_data_quality_report(market_data=market_data, dataset_name="test.csv")
        report2 = build_market_data_quality_report(market_data=market_data, dataset_name="test.csv")

        assert [w["code"] for w in report1["warnings"]] == [w["code"] for w in report2["warnings"]]


class TestExportDataQualityReport:
    def test_exports_json(self, tmp_path):
        report_data = {
            "version": "1.0",
            "exported_at": "2024-01-01T00:00:00Z",
            "generator": "SignalForge",
            "data_source": {
                "symbol": "AAPL",
                "datetime_range": {
                    "start": "2024-01-01T00:00:00Z",
                    "end": "2024-01-02T00:00:00Z",
                },
                "row_count": 100,
            },
            "quality_metrics": {
                "ohlcv_completeness": {
                    "open_null_count": 0,
                    "high_null_count": 0,
                    "low_null_count": 0,
                    "close_null_count": 0,
                    "volume_null_count": 0,
                    "total_rows": 100,
                },
                "price_integrity": {
                    "high_low_violations": 0,
                    "high_open_violations": 0,
                    "low_open_violations": 0,
                },
                "temporal_integrity": {
                    "duplicate_timestamps": 0,
                    "missing_bars": 0,
                },
            },
            "issues": [],
        }

        filepath = export_data_quality_report(report_data, tmp_path)

        assert filepath.name == "data_quality_report.json"
        assert filepath.exists()

        with open(filepath) as f:
            loaded = json.load(f)

        assert loaded["generator"] == "SignalForge"
