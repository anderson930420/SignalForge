"""Tests for CLI module."""

from pathlib import Path


from signalforge.cli import validate_config, build_output_path, check_files_exist


class TestValidateConfig:
    def test_valid_config(self):
        config = {
            "signal_name": "test_signal",
            "source": "test_source",
            "factor_name": "moskowitz_momentum",
            "data_source": {
                "type": "local_ohlcv_csv",
                "path": "/path/to/data.csv",
                "symbol": "AAPL",
            },
            "datetime_range": {
                "start": "2023-01-01",
                "end": "2024-12-31",
            },
            "output": {
                "artifacts_dir": "artifacts",
            },
        }

        errors = validate_config(config)

        assert len(errors) == 0

    def test_missing_signal_name(self):
        config = {
            "source": "test_source",
            "factor_name": "moskowitz_momentum",
            "data_source": {
                "type": "local_ohlcv_csv",
                "path": "/path/to/data.csv",
                "symbol": "AAPL",
            },
            "datetime_range": {
                "start": "2023-01-01",
                "end": "2024-12-31",
            },
            "output": {
                "artifacts_dir": "artifacts",
            },
        }

        errors = validate_config(config)

        assert any("signal_name" in e for e in errors)

    def test_missing_data_source_path(self):
        config = {
            "signal_name": "test_signal",
            "source": "test_source",
            "factor_name": "moskowitz_momentum",
            "data_source": {
                "type": "local_ohlcv_csv",
                "symbol": "AAPL",
            },
            "datetime_range": {
                "start": "2023-01-01",
                "end": "2024-12-31",
            },
            "output": {
                "artifacts_dir": "artifacts",
            },
        }

        errors = validate_config(config)

        assert any("path" in e for e in errors)

    def test_wrong_data_source_type(self):
        config = {
            "signal_name": "test_signal",
            "source": "test_source",
            "factor_name": "moskowitz_momentum",
            "data_source": {
                "type": "database",
                "path": "/path/to/data.csv",
                "symbol": "AAPL",
            },
            "datetime_range": {
                "start": "2023-01-01",
                "end": "2024-12-31",
            },
            "output": {
                "artifacts_dir": "artifacts",
            },
        }

        errors = validate_config(config)

        assert any("local_ohlcv_csv" in e for e in errors)

    def test_missing_datetime_range_end(self):
        config = {
            "signal_name": "test_signal",
            "source": "test_source",
            "factor_name": "moskowitz_momentum",
            "data_source": {
                "type": "local_ohlcv_csv",
                "path": "/path/to/data.csv",
                "symbol": "AAPL",
            },
            "datetime_range": {
                "start": "2023-01-01",
            },
            "output": {
                "artifacts_dir": "artifacts",
            },
        }

        errors = validate_config(config)

        assert any("end" in e for e in errors)

    def test_missing_artifacts_dir(self):
        config = {
            "signal_name": "test_signal",
            "source": "test_source",
            "factor_name": "moskowitz_momentum",
            "data_source": {
                "type": "local_ohlcv_csv",
                "path": "/path/to/data.csv",
                "symbol": "AAPL",
            },
            "datetime_range": {
                "start": "2023-01-01",
                "end": "2024-12-31",
            },
            "output": {},
        }

        errors = validate_config(config)

        assert any("artifacts_dir" in e for e in errors)


class TestBuildOutputPath:
    def test_builds_correct_path(self):
        path = build_output_path(
            artifacts_dir="artifacts",
            symbol="AAPL",
            start_date="2023-01-01",
            end_date="2024-12-31",
        )

        assert path == Path("artifacts/AAPL/20230101_20241231")

    def test_path_is_deterministic(self):
        path1 = build_output_path("artifacts", "AAPL", "2023-01-01", "2024-12-31")
        path2 = build_output_path("artifacts", "AAPL", "2023-01-01", "2024-12-31")

        assert path1 == path2


class TestCheckFilesExist:
    def test_returns_existing_files(self, tmp_path):
        signal_file = tmp_path / "signal.csv"
        signal_file.touch()

        existing = check_files_exist(tmp_path)

        assert signal_file in existing

    def test_returns_empty_when_no_files(self, tmp_path):
        existing = check_files_exist(tmp_path)

        assert len(existing) == 0


class TestCliIntegration:
    """Integration tests for CLI pipeline logic.

    These tests verify the pipeline functions work together correctly.
    Typer CLI invocation tests are limited due to version compatibility issues.
    """

    def test_pipeline_functions_work_together(self, tmp_path):
        from signalforge.data_registry import local_ohlcv_csv
        from signalforge.factor_registry import FactorRegistry
        from signalforge.factors.moskowitz_momentum import MoskowitzMomentumFactor
        from signalforge.signal_composer import SignalComposer
        from signalforge.export import build_signal_contract, build_data_quality_report
        from signalforge.schemas import SignalValidator

        data_csv = tmp_path / "data.csv"
        data_csv.write_text(
            "datetime,open,high,low,close,volume\n"
            "2023-01-01,100,105,99,102,1000000\n"
            "2023-06-01,102,107,101,104,1100000\n"
            "2023-12-01,104,109,103,106,1200000\n"
        )

        data = local_ohlcv_csv(str(data_csv), "AAPL")
        assert len(data) == 3
        assert "symbol" in data.columns
        assert data["symbol"].iloc[0] == "AAPL"

        registry = FactorRegistry()
        registry.register(MoskowitzMomentumFactor())
        factor = registry.get("moskowitz_momentum")

        factor_output = factor.calculate(data)
        assert "factor_value" in factor_output.columns

        composer = SignalComposer()
        composer.set_validator(SignalValidator())
        signal_df = composer.compose(
            factor_output=factor_output,
            datetime=data.iloc[0]["datetime"],
            available_at=data.iloc[0]["datetime"],
            symbol="AAPL",
            signal_name="moskowitz_momentum",
            source="moskowitz_2024",
        )

        assert list(signal_df.columns) == [
            "datetime", "available_at", "symbol", "signal_name",
            "signal_value", "signal_binary", "source"
        ]

        contract = build_signal_contract(
            signal_name="moskowitz_momentum",
            source="moskowitz_2024",
            factor_name="moskowitz_momentum",
            parameters={},
            decision_rule="signal_binary = 1 if signal_value > 0 else 0",
            timing_rule="available_at <= datetime",
            symbols=["AAPL"],
            datetime_range=("2023-01-01", "2023-12-31"),
            row_count=len(signal_df),
            signal_value_stats={"min": 0.1, "max": 0.2, "mean": 0.15, "null_count": 0},
            signal_binary_stats={"value_0_count": 1, "value_1_count": 2, "null_count": 0},
        )

        assert contract["signal_name"] == "moskowitz_momentum"
        assert contract["generator"] == "SignalForge"

        quality_report = build_data_quality_report(
            signal_df=signal_df,
            dataset_name="test.csv",
            source_type="csv",
        )

        assert quality_report["generator"] == "SignalForge"
        assert "signal_value_stats" in quality_report["signals"][0]