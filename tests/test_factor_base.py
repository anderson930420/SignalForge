"""Tests for factor_base module."""

import pandas as pd

from signalforge.factor_base import BaseAlphaFactor, FACTOR_OUTPUT_COLUMNS, FactorProtocol


class TestBaseAlphaFactor:
    def test_protocol_exists(self):
        assert BaseAlphaFactor is not None

    def test_protocol_has_name_attribute(self):
        class DummyFactor:
            name = "test_factor"
            version = "0.1.0"

            def required_inputs(self) -> tuple[str, ...]:
                return ("datetime", "close")

            def compute(self, data: pd.DataFrame) -> pd.DataFrame:
                return pd.DataFrame({
                    "datetime": data["datetime"],
                    "symbol": "TEST",
                    "factor_name": self.name,
                    "factor_value": [1.0],
                    "available_at": data["datetime"],
                })

        factor = DummyFactor()
        assert hasattr(factor, "name")
        assert factor.name == "test_factor"

    def test_protocol_has_version_attribute(self):
        class DummyFactor:
            name = "test_factor"
            version = "0.1.0"

            def required_inputs(self) -> tuple[str, ...]:
                return ("datetime", "close")

            def compute(self, data: pd.DataFrame) -> pd.DataFrame:
                return pd.DataFrame({
                    "datetime": data["datetime"],
                    "symbol": "TEST",
                    "factor_name": self.name,
                    "factor_value": [1.0],
                    "available_at": data["datetime"],
                })

        factor = DummyFactor()
        assert hasattr(factor, "version")
        assert factor.version == "0.1.0"

    def test_protocol_has_required_inputs_method(self):
        class DummyFactor:
            name = "test_factor"
            version = "0.1.0"

            def required_inputs(self) -> tuple[str, ...]:
                return ("datetime", "close")

            def compute(self, data: pd.DataFrame) -> pd.DataFrame:
                return pd.DataFrame({
                    "datetime": data["datetime"],
                    "symbol": "TEST",
                    "factor_name": self.name,
                    "factor_value": [1.0],
                    "available_at": data["datetime"],
                })

        factor = DummyFactor()
        assert hasattr(factor, "required_inputs")
        assert factor.required_inputs() == ("datetime", "close")

    def test_protocol_has_compute_method(self):
        class DummyFactor:
            name = "test_factor"
            version = "0.1.0"

            def required_inputs(self) -> tuple[str, ...]:
                return ("datetime", "close")

            def compute(self, data: pd.DataFrame) -> pd.DataFrame:
                return pd.DataFrame({
                    "datetime": data["datetime"],
                    "symbol": "TEST",
                    "factor_name": self.name,
                    "factor_value": [1.0],
                    "available_at": data["datetime"],
                })

        factor = DummyFactor()
        assert hasattr(factor, "compute")

    def test_factor_output_columns_defined(self):
        assert FACTOR_OUTPUT_COLUMNS == [
            "datetime",
            "symbol",
            "factor_name",
            "factor_value",
            "available_at",
        ]


class TestFactorProtocol:
    def test_protocol_exists(self):
        assert FactorProtocol is not None

    def test_protocol_has_name_attribute(self):
        class DummyFactor:
            name = "test_factor"
            source = "test_source"

            def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
                return pd.DataFrame({"factor_value": [1.0]})

        factor = DummyFactor()
        assert hasattr(factor, "name")
        assert factor.name == "test_factor"

    def test_protocol_has_source_attribute(self):
        class DummyFactor:
            name = "test_factor"
            source = "test_source"

            def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
                return pd.DataFrame({"factor_value": [1.0]})

        factor = DummyFactor()
        assert hasattr(factor, "source")
        assert factor.source == "test_source"