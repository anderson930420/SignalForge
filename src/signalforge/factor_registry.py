"""Factor registration and factor config validation."""

from typing import Any

from signalforge.factor_base import FactorProtocol


class UnknownFactorError(Exception):
    pass


class DuplicateFactorError(Exception):
    pass


class InvalidFactorConfigError(Exception):
    pass


class FactorRegistry:
    """Registry for factor registration and lookup."""

    def __init__(self) -> None:
        self._factors: dict[str, FactorProtocol] = {}

    def register(self, factor: FactorProtocol) -> None:
        """Register a factor.

        Args:
            factor: Factor to register

        Raises:
            DuplicateFactorError: If factor name already registered
        """
        if factor.name in self._factors:
            raise DuplicateFactorError(f"Factor '{factor.name}' already registered")
        self._factors[factor.name] = factor

    def get(self, name: str) -> FactorProtocol:
        """Get a factor by name.

        Args:
            name: Factor name

        Returns:
            Registered factor

        Raises:
            UnknownFactorError: If factor not found
        """
        if name not in self._factors:
            raise UnknownFactorError(f"Unknown factor: '{name}'")
        return self._factors[name]

    def list_factors(self) -> list[str]:
        """List all registered factor names."""
        return list(self._factors.keys())

    def validate_config(self, config: dict[str, Any]) -> bool:
        """Validate factor configuration.

        Args:
            config: Factor configuration dict

        Returns:
            True if valid

        Raises:
            InvalidFactorConfigError: If config is invalid
        """
        if "factors" not in config:
            raise InvalidFactorConfigError("Missing 'factors' key in config")

        for item in config["factors"]:
            if "name" not in item:
                raise InvalidFactorConfigError("Factor config missing 'name'")

        return True
