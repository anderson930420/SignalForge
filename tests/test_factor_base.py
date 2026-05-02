"""Tests for factor_base module."""

import pandas as pd

from signalforge.factor_base import FactorProtocol


class TestFactorProtocol:
    def test_protocol_exists(self):
        assert FactorProtocol is not None

    def test_protocol_has_name_attribute(self):
        class DummyFactor:
            name = "test_factor"
            source = "test_source"

            def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
                return pd.DataFrame({"signal_value": [1.0]})

        factor = DummyFactor()
        assert hasattr(factor, "name")
        assert factor.name == "test_factor"

    def test_protocol_has_source_attribute(self):
        class DummyFactor:
            name = "test_factor"
            source = "test_source"

            def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
                return pd.DataFrame({"signal_value": [1.0]})

        factor = DummyFactor()
        assert hasattr(factor, "source")
        assert factor.source == "test_source"