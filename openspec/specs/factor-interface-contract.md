# Factor Interface Contract

## Type

Capability Specification

## Purpose

Define the protocol for factor implementations in SignalForge.

## Owner

SignalForge

## Protocol Definition

All factor implementations must conform to the FactorProtocol defined in `factor_base.py`.

## Protocol Interface

```python
class FactorProtocol:
    name: str
    source: str

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate factor values from OHLCV data.

        Args:
            data: DataFrame with OHLCV columns (datetime, open, high, low, close, volume)

        Returns:
            DataFrame with factor values (must include 'signal_value' column)
        """
        ...
```

## Required Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| name | str | Unique identifier for the factor |
| source | str | Source identifier (e.g., "moskowitz_2024") |

## Required Methods

### calculate(data: pd.DataFrame) -> pd.DataFrame

| Aspect | Requirement |
|--------|-------------|
| Input | DataFrame with OHLCV columns (datetime, open, high, low, close, volume) |
| Output | DataFrame with 'signal_value' column and same index as input |
| Pure function | Must not modify input DataFrame |
| Null handling | Null signal_value must be explicit (not silently dropped) |

## Output Schema

The returned DataFrame must contain:

| Column | Type | Description |
|--------|------|-------------|
| signal_value | float | Factor output value |

And may contain:

| Column | Type | Description |
|--------|------|-------------|
| signal_binary | int | Optional binary signal (0 or 1) |

## Constraints

- Factor must be pure (no side effects, no state modification)
- Factor must handle null OHLCV values gracefully
- Factor calculation must be deterministic (same input = same output)

## Implementation Location

Factor implementations reside in `factors/` directory.

## Example Factors (MVP)

- Moskowitz Momentum Factor (see moskowitz-momentum-factor spec)
