"""Tests for export module."""

import json

import pandas as pd
import yaml

from signalforge.export import (
    export_signal_csv,
    export_signal_contract_yaml,
    export_data_quality_report,
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
        assert len(loaded["signals"]) == 1


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