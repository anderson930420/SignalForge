# Signal Artifact Contract

## Type

Capability Specification

## Purpose

Define the canonical schema for signal.csv artifacts produced by SignalForge.

## Owner

SignalForge

## Artifact Schema

SignalForge exports signal artifacts as CSV with the following required column order:

| Column | Type | Description | Constraints |
|--------|------|-------------|-------------|
| datetime | ISO 8601 timestamp | Timestamp of the signal | Not null |
| available_at | ISO 8601 timestamp | When the signal became available | Must be <= datetime |
| symbol | string | Ticker symbol | Not null |
| signal_name | string | Name of the signal/factor | Not null |
| signal_value | float | Continuous signal value | May be null |
| signal_binary | integer | Binary signal (0 or 1) | Only 0 or 1 |
| source | string | Source identifier for the factor | Not null |

## Column Order

The columns must appear in the specified order:

1. datetime
2. available_at
3. symbol
4. signal_name
5. signal_value
6. signal_binary
7. source

## Constraints

### Temporal Constraint

`available_at <= datetime` for all rows. A signal cannot be available after the timestamp it is associated with.

### Binary Signal Constraint

`signal_binary` column must only contain values 0 or 1. No other values permitted.

### Uniqueness Constraint

No duplicate `(datetime, symbol, signal_name)` rows permitted. Each combination must be unique.

### Nullability Constraints

- datetime: NOT NULL
- available_at: NOT NULL
- symbol: NOT NULL
- signal_name: NOT NULL
- signal_value: MAY BE NULL (for signals without continuous value)
- signal_binary: NOT NULL
- source: NOT NULL

## Export Location

signal.csv must be written to the configured artifacts directory with deterministic file layout.

## AlphaForge Compatibility

This schema is compatible with AlphaForge custom_signal interface. Schema validation is pure Python (no AlphaForge import).
