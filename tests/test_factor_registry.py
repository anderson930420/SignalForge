"""Tests for factor_registry module."""

import pandas as pd
import pytest

from signalforge.factor_registry import (
    FactorRegistry,
    UnknownFactorError,
    DuplicateFactorError,
    InvalidFactorConfigError,
)


class DummyCanonicalFactor:
    name = "dummy_factor"
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

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        return pd.DataFrame({"factor_value": [1.0]})


class AnotherCanonicalFactor:
    name = "another_factor"
    version = "0.1.0"

    def required_inputs(self) -> tuple[str, ...]:
        return ("datetime", "close")

    def compute(self, data: pd.DataFrame) -> pd.DataFrame:
        return pd.DataFrame({
            "datetime": data["datetime"],
            "symbol": "TEST",
            "factor_name": self.name,
            "factor_value": [2.0],
            "available_at": data["datetime"],
        })

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        return pd.DataFrame({"factor_value": [2.0]})


class LegacyFactor:
    name = "legacy_factor"
    source = "legacy_source"

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        return pd.DataFrame({"factor_value": [3.0]})


class TestFactorRegistry:
    def test_register_and_get(self):
        registry = FactorRegistry()
        factor = DummyCanonicalFactor()

        registry.register(factor)
        retrieved = registry.get("dummy_factor")

        assert retrieved is factor

    def test_get_factor_alias(self):
        registry = FactorRegistry()
        factor = DummyCanonicalFactor()

        registry.register(factor)
        retrieved = registry.get_factor("dummy_factor")

        assert retrieved is factor

    def test_rejects_duplicate_factor(self):
        registry = FactorRegistry()
        factor = DummyCanonicalFactor()

        registry.register(factor)

        with pytest.raises(DuplicateFactorError):
            registry.register(factor)

    def test_raises_unknown_factor_error(self):
        registry = FactorRegistry()

        with pytest.raises(UnknownFactorError):
            registry.get("nonexistent_factor")

    def test_get_factor_raises_unknown_factor_error(self):
        registry = FactorRegistry()

        with pytest.raises(UnknownFactorError):
            registry.get_factor("nonexistent_factor")

    def test_list_factors(self):
        registry = FactorRegistry()
        registry.register(DummyCanonicalFactor())
        registry.register(AnotherCanonicalFactor())

        factors = registry.list_factors()

        assert "dummy_factor" in factors
        assert "another_factor" in factors

    def test_validate_factor_config_valid(self):
        registry = FactorRegistry()
        registry.register(DummyCanonicalFactor())

        result = registry.validate_factor_config("dummy_factor", {"datetime": None, "close": None})

        assert result is True

    def test_validate_factor_config_unknown_factor(self):
        registry = FactorRegistry()

        with pytest.raises(UnknownFactorError):
            registry.validate_factor_config("nonexistent", {})

    def test_validate_factor_config_missing_inputs(self):
        registry = FactorRegistry()
        registry.register(DummyCanonicalFactor())

        with pytest.raises(InvalidFactorConfigError):
            registry.validate_factor_config("dummy_factor", {"datetime": None})

    def test_validate_factor_config_not_dict(self):
        registry = FactorRegistry()
        registry.register(DummyCanonicalFactor())

        with pytest.raises(InvalidFactorConfigError):
            registry.validate_factor_config("dummy_factor", "not_a_dict")

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