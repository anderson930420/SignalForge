# Factor Registry Contract

## Type

Capability Specification

## Purpose

Define the factor registry that manages factor registration, configuration validation, and lookup.

## Owner

SignalForge

## Component Location

`factor_registry.py` owns factor registration and factor config validation.

## Registry Interface

```python
class FactorRegistry:
    def register(self, factor: FactorProtocol) -> None:
        """Register a factor."""
        ...

    def get(self, name: str) -> FactorProtocol:
        """Get a factor by name."""
        ...

    def list_factors(self) -> list[str]:
        """List all registered factor names."""
        ...

    def validate_config(self, config: dict) -> bool:
        """Validate factor configuration."""
        ...
```

## Registration Rules

| Rule | Behavior |
|------|----------|
| Unknown factor requested | Raise UnknownFactorError |
| Duplicate factor registration | Raise DuplicateFactorError |
| Invalid factor config | Raise InvalidFactorConfigError |

## Error Types

| Error | Condition |
|-------|-----------|
| UnknownFactorError | Attempting to get a factor not in registry |
| DuplicateFactorError | Attempting to register a factor with existing name |
| InvalidFactorConfigError | Factor config does not match expected schema |

## Configuration Schema

```yaml
factors:
  - name: string  # Factor name (must match FactorProtocol.name)
    enabled: boolean  # Whether factor is active
    params: dict  # Factor-specific parameters
```

## MVP Scope

MVP registry supports:
- In-memory factor storage
- Synchronous registration and lookup
- Basic config validation

Future capabilities (non-MVP):
- Persistent registry
- Factor versioning
- Plugin discovery

## Testing Requirements

- FactorRegistry rejects unknown factors
- FactorRegistry rejects duplicate registrations
- FactorRegistry validates config schema
