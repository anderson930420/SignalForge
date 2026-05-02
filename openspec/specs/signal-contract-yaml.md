# Signal Contract YAML

## Type

Capability Specification

## Purpose

Define the schema and structure of signal_contract.yaml artifacts exported by SignalForge.

## Owner

SignalForge

## Artifact Location

signal_contract.yaml is co-located with signal.csv in the artifacts directory.

## YAML Schema

```yaml
version: string  # Contract version (e.g., "1.0")
exported_at: ISO 8601 timestamp  # When the contract was generated
generator: string  # "SignalForge"
signals: list[SignalEntry]
```

### SignalEntry Schema

```yaml
- signal_name: string  # Name of the signal/factor
  source: string  # Source identifier
  symbols: list[string]  # List of symbols covered
  datetime_range:
    start: ISO 8601 timestamp
    end: ISO 8601 timestamp
  row_count: integer  # Number of rows for this signal
  signal_value_stats:
    min: float
    max: float
    mean: float
    null_count: integer
  signal_binary_stats:
    value_0_count: integer
    value_1_count: integer
    null_count: integer
```

## Required Fields

- version: Required
- exported_at: Required
- generator: Required, must be "SignalForge"
- signals: Required, non-empty list

## Constraints

- signals list must be non-empty
- datetime_range.start <= datetime_range.end for each entry
- signal_binary_stats.value_0_count + signal_binary_stats.value_1_count + signal_binary_stats.null_count must equal row_count

## Purpose

The signal_contract.yaml provides metadata about the signal artifacts, enabling downstream consumers (like AlphaForge) to understand the signal composition before consuming signal.csv.
