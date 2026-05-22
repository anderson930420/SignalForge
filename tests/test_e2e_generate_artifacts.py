"""End-to-end test for signal artifact generation."""

from pathlib import Path

import numpy as np
import pandas as pd
import yaml


class TestE2EGenerateArtifacts:
    """End-to-end test for CLI artifact generation pipeline."""

    def test_e2e_generate_artifacts(self, tmp_path: Path) -> None:
        """Test full pipeline from config to artifact generation."""
        from signalforge.data_registry import local_ohlcv_csv
        from signalforge.factor_registry import FactorRegistry
        from signalforge.factors.moskowitz_momentum import MoskowitzMomentumFactor
        from signalforge.signal_composer import SignalComposer
        from signalforge.export import (
            export_signal_csv,
            export_signal_contract_yaml,
            export_data_quality_report,
            build_signal_contract,
            build_market_data_quality_report,
        )
        from signalforge.schemas import SignalValidator

        start_date = "2021-01-04"
        end_date = "2024-12-31"

        bdays = pd.bdate_range(start=start_date, end=end_date)
        n_rows = len(bdays)
        assert n_rows >= 700, f"Need 700+ business days for 252-day lookback, got {n_rows}"

        base_price = 100.0
        np.random.seed(42)
        returns = np.random.normal(0.0005, 0.02, n_rows)
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

        csv_path = tmp_path / "data.csv"
        ohlcv_df.to_csv(csv_path, index=False)

        signal_name = "moskowitz_momentum"
        source = "moskowitz_2024"
        symbol = "AAPL"

        data = local_ohlcv_csv(str(csv_path), symbol)

        filter_start = "2023-01-01"
        filter_end = "2024-12-31"
        if "datetime" in data.columns:
            data = data[(data["datetime"] >= filter_start) & (data["datetime"] <= filter_end)]
        data = data.reset_index(drop=True)

        assert len(data) > 0, "Filtered data is empty"

        registry = FactorRegistry()
        registry.register(MoskowitzMomentumFactor())
        factor = registry.get(signal_name)
        factor_output = factor.calculate(data)

        composer = SignalComposer()
        composer.set_validator(SignalValidator())

        signal_df = composer.compose(
            factor_output=factor_output,
            datetime=data["datetime"],
            available_at=data["datetime"],
            symbol=symbol,
            signal_name=signal_name,
            source=source,
        )

        assert len(signal_df) == len(data), (
            f"signal.csv row count should match selected OHLCV data rows, got {len(signal_df)} vs {len(data)}"
        )
        assert signal_df["signal_binary"].isin([0, 1]).all(), "signal_binary contains non-binary values"
        assert signal_df["signal_value"].isnull().any(), "warmup rows should preserve null signal_value"
        assert (signal_df["signal_binary"] == 0).any(), "warmup rows should emit binary 0"
        assert (signal_df["available_at"] <= signal_df["datetime"]).all(), "available_at > datetime violation found"
        assert signal_df["datetime"].tolist() == data["datetime"].tolist(), "signal dates must match selected market dates"
        assert not signal_df.duplicated(subset=["datetime", "symbol", "signal_name"]).any()

        output_dir = tmp_path / "artifacts" / symbol / signal_name / "20230101_20241231"
        output_dir.mkdir(parents=True, exist_ok=True)

        signal_value_stats = {
            "min": float(factor_output["factor_value"].min()) if not factor_output["factor_value"].isnull().all() else None,
            "max": float(factor_output["factor_value"].max()) if not factor_output["factor_value"].isnull().all() else None,
            "mean": float(factor_output["factor_value"].mean()) if not factor_output["factor_value"].isnull().all() else None,
            "null_count": int(factor_output["factor_value"].isnull().sum()),
        }

        signal_binary_stats = {
            "value_0_count": int((signal_df["signal_binary"] == 0).sum()),
            "value_1_count": int((signal_df["signal_binary"] == 1).sum()),
            "null_count": int(signal_df["signal_binary"].isnull().sum()),
        }

        contract = build_signal_contract(
            signal_name=signal_name,
            source=source,
            factor_name=signal_name,
            parameters={},
            decision_rule="signal_binary = 1 if signal_value > 0 else 0",
            timing_rule="same declared daily trading date as datetime for OHLCV-only daily signal",
            symbols=[symbol],
            datetime_range=(filter_start, filter_end),
            row_count=len(signal_df),
            signal_value_stats=signal_value_stats,
            signal_binary_stats=signal_binary_stats,
            symbol=symbol,
            frequency="daily",
            input_data={
                "type": "local_ohlcv_csv",
                "path": str(csv_path),
                "required_columns": [
                    "datetime",
                    "open",
                    "high",
                    "low",
                    "close",
                    "volume",
                ],
            },
        )

        quality_report = build_market_data_quality_report(
            market_data=data,
            dataset_name=str(csv_path),
            source_type="local_ohlcv_csv",
        )

        export_signal_csv(signal_df, output_dir, validate=True)
        export_signal_contract_yaml(contract, output_dir)
        export_data_quality_report(quality_report, output_dir)

        signal_csv_path = output_dir / "signal.csv"
        signal_contract_path = output_dir / "signal_contract.yaml"
        quality_report_path = output_dir / "data_quality_report.json"

        assert signal_csv_path.exists(), "signal.csv not found"
        assert signal_contract_path.exists(), "signal_contract.yaml not found"
        assert quality_report_path.exists(), "data_quality_report.json not found"

        result_df = pd.read_csv(signal_csv_path)
        required_columns = [
            "datetime",
            "available_at",
            "symbol",
            "signal_name",
            "signal_value",
            "signal_binary",
            "source",
        ]
        assert list(result_df.columns) == required_columns, (
            f"Column mismatch: {list(result_df.columns)}"
        )
        assert len(result_df) == len(data), f"Need {len(data)} rows, got {len(result_df)}"

        assert result_df["signal_binary"].isin([0, 1]).all(), (
            "signal_binary contains values other than 0 or 1"
        )

        result_df["datetime"] = pd.to_datetime(result_df["datetime"])
        result_df["available_at"] = pd.to_datetime(result_df["available_at"])
        assert (result_df["available_at"] <= result_df["datetime"]).all(), (
            "available_at > datetime violation found"
        )

        dup_mask = result_df.duplicated(
            subset=["datetime", "symbol", "signal_name"],
            keep=False,
        )
        assert not dup_mask.any(), "Duplicate datetime-symbol-signal_name rows found"

        contract_data = yaml.safe_load(signal_contract_path.read_text(encoding="utf-8"))
        assert contract_data["signal_name"] == signal_name
        assert contract_data["source"] == source
        assert contract_data["version"] == "0.1.0"
        assert "factor" in contract_data
        assert contract_data["factor"]["name"] == signal_name
        assert contract_data["factor"]["version"] == "0.1.0"
        assert "decision_rule" in contract_data
        assert "signal_binary" in contract_data["decision_rule"]
        assert "timing" in contract_data
        assert "available_at_rule" in contract_data["timing"]
        assert "output" in contract_data
        assert contract_data["output"]["file"] == "signal.csv"
        assert contract_data["output"]["schema_version"] == "0.1.0"
        assert contract_data["output"]["columns"] == required_columns

        quality_data = yaml.safe_load(quality_report_path.read_text(encoding="utf-8"))
        assert quality_data.get("source_type") == "local_ohlcv_csv", (
            f"source_type mismatch: {quality_data.get('source_type')}"
        )
        assert quality_data.get("symbol_count") == 1, (
            f"symbol_count mismatch: {quality_data.get('symbol_count')}"
        )
        assert quality_data.get("row_count") == len(data), (
            f"row_count mismatch: expected {len(data)}, got {quality_data.get('row_count')}"
        )
        assert "start_date" in quality_data, "start_date missing"
        assert "end_date" in quality_data, "end_date missing"
        assert "duplicate_rows" in quality_data, "duplicate_rows missing"
        assert "missing_values" in quality_data, "missing_values missing"
        assert "warnings" in quality_data, "warnings missing"
        assert isinstance(quality_data.get("missing_values"), dict), "missing_values should be a dict"
        assert quality_data.get("point_in_time_correctness_claimed") is False

    def test_e2e_alphaforge_contract_requirements(self, tmp_path: Path) -> None:
        """Verify the generated signal.csv satisfies AlphaForge custom_signal contract."""
        self.test_e2e_generate_artifacts(tmp_path)

        result_df = pd.read_csv(
            tmp_path
            / "artifacts"
            / "AAPL"
            / "moskowitz_momentum"
            / "20230101_20241231"
            / "signal.csv"
        )

        assert not result_df["signal_binary"].isnull().any(), (
            "signal_binary has missing values"
        )

        invalid_binary = ~result_df["signal_binary"].isin([0, 1])
        assert not invalid_binary.any(), (
            f"signal_binary has invalid values: {result_df[invalid_binary]['signal_binary'].unique()}"
        )

        result_df["datetime"] = pd.to_datetime(result_df["datetime"])
        result_df["available_at"] = pd.to_datetime(result_df["available_at"])

        temporal_violations = result_df[result_df["available_at"] > result_df["datetime"]]
        assert len(temporal_violations) == 0, (
            f"Found {len(temporal_violations)} rows with available_at > datetime"
        )

        dup_mask = result_df.duplicated(
            subset=["datetime", "symbol", "signal_name"],
            keep=False,
        )
        dup_rows = result_df[dup_mask]
        assert len(dup_rows) == 0, (
            f"Found {len(dup_rows)} duplicate datetime-symbol-signal_name rows"
        )

        assert len(result_df) > 1, (
            "AlphaForge compatibility requires multiple rows"
        )
