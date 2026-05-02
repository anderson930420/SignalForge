# Signal Composer Contract

## Type

Capability Specification

## Purpose

Define the signal composer that converts factor outputs into signal artifact rows.

## Owner

SignalForge

## Component Location

`signal_composer.py` owns conversion from factor output to signal artifact rows.

## Composition Rules

### Input

- Factor output DataFrame (from FactorProtocol.calculate)
- Factor metadata (name, source)
- Timestamp metadata (datetime, available_at)

### Output

- DataFrame conforming to signal-artifact-contract schema

### Required Columns

| Column | Source |
|--------|--------|
| datetime | From input metadata |
| available_at | From input metadata |
| symbol | From input metadata |
| signal_name | From factor.name |
| signal_value | From factor output 'signal_value' column |
| signal_binary | Derived from signal_value or explicit from factor |
| source | From factor.source |

## Binary Signal Derivation

If factor does not provide explicit signal_binary:

- signal_value > 0 -> signal_binary = 1
- signal_value <= 0 -> signal_binary = 0

## Composition Flow

1. Receive factor output DataFrame
2. Attach metadata (datetime, available_at, symbol, signal_name, source)
3. Validate required columns present
4. Derive signal_binary if not provided
5. Ensure column order matches signal-artifact-contract

## Constraints

- Must not modify factor output DataFrame (copy if needed)
- Must preserve all rows from factor output
- Null signal_value must be preserved (not filtered)
- datetime must be parseable as ISO 8601

## Testing Requirements

- Composer produces correct column order
- Composer preserves null signal_value rows
- Composer derives signal_binary correctly when not explicit
