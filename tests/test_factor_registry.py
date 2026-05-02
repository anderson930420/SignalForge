"""Tests for factor_registry module."""

import pandas as pd
import pytest

from signalforge.factor_registry import (
    FactorRegistry,
    UnknownFactorError,
    DuplicateFactorError,
    InvalidFactorConfigError,
)


class DummyFactor:
    name = "dummy_factor"
    source = "dummy_source"

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        return pd.DataFrame({"signal_value": [1.0]})


class AnotherFactor:
    name = "another_factor"
    source = "another_source"

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        return pd.DataFrame({"signal_value": [2.0]})


class TestFactorRegistry:
    def test_register_and_get(self):
        registry = FactorRegistry()
        factor = DummyFactor()

        registry.register(factor)
        retrieved = registry.get("dummy_factor")

        assert retrieved is factor

    def test_rejects_duplicate_factor(self):
        registry = FactorRegistry()
        factor = DummyFactor()

        registry.register(factor)

        with pytest.raises(DuplicateFactorError):
            registry.register(factor)

    def test_raises_unknown_factor_error(self):
        registry = FactorRegistry()

        with pytest.raises(UnknownFactorError):
            registry.get("nonexistent_factor")

    def test_list_factors(self):
        registry = FactorRegistry()
        registry.register(DummyFactor())
        registry.register(AnotherFactor())

        factors = registry.list_factors()

        assert "dummy_factor" in factors
        assert "another_factor" in factors

    def test_validate_config_valid(self):
        registry = FactorRegistry()
        config = {
            "factors": [
                {"name": "factor1", "enabled": True},
            ]
        }

        result = registry.validate_config(config)

        assert result is True

    def test_validate_config_missing_factors_key(self):
        registry = FactorRegistry()
        config = {}

        with pytest.raises(InvalidFactorConfigError):
            registry.validate_config(config)

    def test_validate_config_missing_name(self):
        registry = FactorRegistry()
        config = {
            "factors": [
                {"enabled": True},
            ]
        }

        with pytest.raises(InvalidFactorConfigError):
            registry.validate_config(config)