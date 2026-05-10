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
            signal_name="moskowitz_momentum",
            start_date="2023-01-01",
            end_date="2024-12-31",
        )

        assert path == Path("artifacts/AAPL/moskowitz_momentum/20230101_20241231")

    def test_path_is_deterministic(self):
        path1 = build_output_path("artifacts", "AAPL", "moskowitz_momentum", "2023-01-01", "2024-12-31")
        path2 = build_output_path("artifacts", "AAPL", "moskowitz_momentum", "2023-01-01", "2024-12-31")

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
            datetime=data["datetime"],
            available_at=data["datetime"],
            symbol="AAPL",
            signal_name="moskowitz_momentum",
            source="moskowitz_2024",
        )

        assert list(signal_df.columns) == [
            "datetime", "available_at", "symbol", "signal_name",
            "signal_value", "signal_binary", "source"
        ]
        assert len(signal_df) == len(data)
        assert signal_df["signal_binary"].isin([0, 1]).all()
        assert (signal_df["available_at"] <= signal_df["datetime"]).all()
        assert signal_df["datetime"].tolist() == data["datetime"].tolist()

        contract = build_signal_contract(
            signal_name="moskowitz_momentum",
            source="moskowitz_2024",
            factor_name="moskowitz_momentum",
            parameters={},
            decision_rule="1 if signal_value > 0 else 0",
            timing_rule="same as datetime for OHLCV-only daily signal",
            symbols=["AAPL"],
            datetime_range=("2023-01-01", "2023-12-31"),
            row_count=len(signal_df),
            signal_value_stats={"min": 0.1, "max": 0.2, "mean": 0.15, "null_count": 0},
            signal_binary_stats={"value_0_count": 1, "value_1_count": 2, "null_count": 0},
            symbol="AAPL",
            frequency="daily",
            factor_version="0.1.0",
        )

        assert contract["signal_name"] == "moskowitz_momentum"
        assert contract["version"] == "0.1.0"
        assert "factor" in contract
        assert contract["factor"]["name"] == "moskowitz_momentum"
        assert contract["factor"]["version"] == "0.1.0"
        assert "decision_rule" in contract
        assert "signal_binary" in contract["decision_rule"]
        assert contract["decision_rule"]["signal_binary"] == "1 if signal_value > 0 else 0"
        assert "timing" in contract
        assert "available_at_rule" in contract["timing"]
        assert "output" in contract
        assert contract["output"]["file"] == "signal.csv"
        assert contract["output"]["schema_version"] == "0.1.0"
        assert contract["output"]["columns"] == [
            "datetime",
            "available_at",
            "symbol",
            "signal_name",
            "signal_value",
            "signal_binary",
            "source",
        ]

        quality_report = build_data_quality_report(
            signal_df=signal_df,
            dataset_name="test.csv",
            source_type="csv",
        )

        assert quality_report["generator"] == "SignalForge"
        assert quality_report["row_count"] == len(signal_df)
        assert "signal_value_stats" in quality_report["signals"][0]


class TestGenerateCommand:
    """CLI generate command integration tests."""

    def test_generate_produces_all_three_artifacts(self, tmp_path: Path) -> None:
        """Test that signalforge generate --config --overwrite produces all three artifacts."""
        import numpy as np
        import pandas as pd
        import yaml

        start_date = "2021-01-04"
        end_date = "2024-12-31"
        bdays = pd.bdate_range(start=start_date, end=end_date)
        n_rows = len(bdays)
        assert n_rows >= 700, f"Need 700+ business days for 252-day lookback, got {n_rows}"

        np.random.seed(42)
        returns = np.random.normal(0.0005, 0.02, n_rows)
        base_price = 100.0
        close_prices = base_price * (1 + returns).cumprod()
        high_prices = close_prices * (1 + np.abs(np.random.normal(0, 0.01, n_rows)))
        low_prices = close_prices * (1 - np.abs(np.random.normal(0, 0.01, n_rows)))
        open_prices = np.roll(close_prices, 1)
        open_prices[0] = base_price
        volumes = np.random.randint(1_000_000, 10_000_000, n_rows)

        ohlcv_df = pd.DataFrame({
            "datetime": bdays,
            "open": open_prices,
            "high": high_prices,
            "low": low_prices,
            "close": close_prices,
            "volume": volumes,
        })

        csv_path = tmp_path / "ohlcv.csv"
        ohlcv_df.to_csv(csv_path, index=False)

        config = {
            "signal_name": "moskowitz_momentum",
            "source": "moskowitz_2024",
            "factor_name": "moskowitz_momentum",
            "factor_params": {"lookback_days": 252, "skip_days": 21},
            "data_source": {
                "type": "local_ohlcv_csv",
                "path": str(csv_path),
                "symbol": "AAPL",
            },
            "datetime_range": {
                "start": "2021-01-04T00:00:00Z",
                "end": "2024-12-31T23:59:59Z",
            },
            "output": {
                "artifacts_dir": str(tmp_path / "artifacts"),
            },
        }

        config_path = tmp_path / "signal_config.yaml"
        with open(config_path, "w") as f:
            yaml.dump(config, f)

        from typer.testing import CliRunner
        from signalforge.cli import app

        runner = CliRunner()
        result = runner.invoke(app, ["--config", str(config_path), "--overwrite"])
        assert result.exit_code == 0, f"CLI failed: {result.output}\n{result.exception}"

        output_dir = tmp_path / "artifacts" / "AAPL" / "moskowitz_momentum" / "20210104_20241231"

        assert (output_dir / "signal.csv").exists(), f"signal.csv not found at {output_dir}"
        assert (output_dir / "signal_contract.yaml").exists(), f"signal_contract.yaml not found at {output_dir}"
        assert (output_dir / "data_quality_report.json").exists(), f"data_quality_report.json not found at {output_dir}"

        signal_df = pd.read_csv(output_dir / "signal.csv")
        required_columns = ["datetime", "available_at", "symbol", "signal_name", "signal_value", "signal_binary", "source"]
        assert list(signal_df.columns) == required_columns, f"Column mismatch: {list(signal_df.columns)}"
        assert len(signal_df) > 1, f"Expected more than one row, got {len(signal_df)}"
        assert signal_df["signal_binary"].isin([0, 1]).all(), "signal_binary contains non-binary values"

        signal_df["datetime"] = pd.to_datetime(signal_df["datetime"])
        signal_df["available_at"] = pd.to_datetime(signal_df["available_at"])
        assert (signal_df["available_at"] <= signal_df["datetime"]).all(), "available_at > datetime violation found"

        dup_mask = signal_df.duplicated(subset=["datetime", "symbol", "signal_name"], keep=False)
        assert not dup_mask.any(), "Duplicate datetime-symbol-signal_name rows found"

        assert not pd.read_csv(output_dir / "signal.csv").columns.str.contains("alpha").any()

    def test_generate_overwrite_replaces_existing_files(self, tmp_path: Path) -> None:
        """Test that --overwrite replaces existing files."""
        import numpy as np
        import pandas as pd
        import yaml

        bdays = pd.bdate_range(start="2021-01-04", end="2024-12-31")
        n_rows = len(bdays)

        np.random.seed(42)
        returns = np.random.normal(0.0005, 0.02, n_rows)
        base_price = 100.0
        close_prices = base_price * (1 + returns).cumprod()

        ohlcv_df = pd.DataFrame({
            "datetime": bdays,
            "open": close_prices * 0.99,
            "high": close_prices * 1.01,
            "low": close_prices * 0.98,
            "close": close_prices,
            "volume": np.random.randint(1_000_000, 10_000_000, n_rows),
        })

        csv_path = tmp_path / "ohlcv.csv"
        ohlcv_df.to_csv(csv_path, index=False)

        config = {
            "signal_name": "moskowitz_momentum",
            "source": "moskowitz_2024",
            "factor_name": "moskowitz_momentum",
            "factor_params": {},
            "data_source": {
                "type": "local_ohlcv_csv",
                "path": str(csv_path),
                "symbol": "AAPL",
            },
            "datetime_range": {
                "start": "2021-01-04T00:00:00Z",
                "end": "2024-12-31T23:59:59Z",
            },
            "output": {
                "artifacts_dir": str(tmp_path / "artifacts"),
            },
        }

        config_path = tmp_path / "signal_config.yaml"
        with open(config_path, "w") as f:
            yaml.dump(config, f)

        from typer.testing import CliRunner
        from signalforge.cli import app

        runner = CliRunner()

        result1 = runner.invoke(app, ["--config", str(config_path), "--overwrite"])
        assert result1.exit_code == 0, f"First run failed: {result1.output}"

        output_dir = tmp_path / "artifacts" / "AAPL" / "moskowitz_momentum" / "20210104_20241231"
        first_mtime = (output_dir / "signal.csv").stat().st_mtime

        import time
        time.sleep(0.1)

        result2 = runner.invoke(app, ["--config", str(config_path), "--overwrite"])
        assert result2.exit_code == 0, f"Second run with overwrite failed: {result2.output}"

        second_mtime = (output_dir / "signal.csv").stat().st_mtime
        assert second_mtime >= first_mtime, "File should have been overwritten"

    def test_generate_without_overwrite_preserves_files(self, tmp_path: Path) -> None:
        """Test that running without --overwrite preserves existing files."""
        import numpy as np
        import pandas as pd
        import yaml

        bdays = pd.bdate_range(start="2021-01-04", end="2024-12-31")
        n_rows = len(bdays)

        np.random.seed(42)
        returns = np.random.normal(0.0005, 0.02, n_rows)
        base_price = 100.0
        close_prices = base_price * (1 + returns).cumprod()

        ohlcv_df = pd.DataFrame({
            "datetime": bdays,
            "open": close_prices * 0.99,
            "high": close_prices * 1.01,
            "low": close_prices * 0.98,
            "close": close_prices,
            "volume": np.random.randint(1_000_000, 10_000_000, n_rows),
        })

        csv_path = tmp_path / "ohlcv.csv"
        ohlcv_df.to_csv(csv_path, index=False)

        config = {
            "signal_name": "moskowitz_momentum",
            "source": "moskowitz_2024",
            "factor_name": "moskowitz_momentum",
            "factor_params": {},
            "data_source": {
                "type": "local_ohlcv_csv",
                "path": str(csv_path),
                "symbol": "AAPL",
            },
            "datetime_range": {
                "start": "2021-01-04T00:00:00Z",
                "end": "2024-12-31T23:59:59Z",
            },
            "output": {
                "artifacts_dir": str(tmp_path / "artifacts"),
            },
        }

        config_path = tmp_path / "signal_config.yaml"
        with open(config_path, "w") as f:
            yaml.dump(config, f)

        from typer.testing import CliRunner
        from signalforge.cli import app

        runner = CliRunner()

        result1 = runner.invoke(app, ["--config", str(config_path), "--overwrite"])
        assert result1.exit_code == 0, f"First run failed: {result1.output}"

        output_dir = tmp_path / "artifacts" / "AAPL" / "moskowitz_momentum" / "20210104_20241231"
        first_mtime = (output_dir / "signal.csv").stat().st_mtime

        result2 = runner.invoke(app, ["--config", str(config_path)])
        assert result2.exit_code != 0, "Should have failed without --overwrite"
        assert "Use --overwrite to replace" in result2.output

        second_mtime = (output_dir / "signal.csv").stat().st_mtime
        assert second_mtime == first_mtime, "File should not have been modified"
