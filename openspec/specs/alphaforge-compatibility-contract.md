# AlphaForge Compatibility Contract

## Type

Capability Specification

## Purpose

Define pure schema validation checks for AlphaForge-compatible signal artifacts.

## Owner

SignalForge

## Component Location

`compatibility.py` owns pure AlphaForge-compatible schema checks.

## Compatibility Scope

SignalForge provides schema validation that AlphaForge can rely on without importing AlphaForge. This is pure Python validation.

## Schema Validation Checks

### signal.csv Validation

| Check | Expected Value |
|-------|---------------|
| Column count | 7 |
| Column order | datetime, available_at, symbol, signal_name, signal_value, signal_binary, source |
| datetime format | ISO 8601 |
| available_at format | ISO 8601 |
| signal_binary values | Only 0 or 1 |
| available_at <= datetime | Must hold for all rows |
| Null constraints | datetime, available_at, symbol, signal_name, signal_binary, source NOT NULL |

### signal_contract.yaml Validation

| Check | Expected Value |
|-------|---------------|
| Top-level keys | version, exported_at, generator, signals |
| generator value | "SignalForge" |
| signals type | non-empty list |
| signal entries | signal_name, source, symbols, datetime_range, row_count |

### Cross-Artifact Validation

| Check | Expected Value |
|-------|---------------|
| signals in contract match data | symbol counts consistent |
| datetime_range alignment | Contract datetime_range matches signal.csv data range |

## Explicit Non-Imports

SignalForge MVP must not import AlphaForge. Compatibility validation is implemented as pure Python functions.

## AlphaForge Interface

SignalForge signal.csv artifacts are designed for AlphaForge custom_signal interface consumption. This schema compatibility enables downstream validation by AlphaForge.

## Testing Constraints

MVP unit tests must not import AlphaForge. All compatibility checks are implemented within SignalForge codebase.

## Error Reporting

Validation errors must include:
- The specific check that failed
- The artifact (signal.csv, signal_contract.yaml, or data_quality_report.json)
- The affected row or field (if applicable)
