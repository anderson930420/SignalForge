# Project Boundary

## Type

Capability Specification

## Purpose

Define the ownership boundary of SignalForge MVP, excluding concerns owned by other systems.

## Owner

SignalForge

## Boundary Definition

SignalForge is a paper-derived factor and standardized signal generation layer. It transforms input market data and factor definitions into standardized signal artifacts for downstream consumption by AlphaForge.

## SignalForge Owns

| Concern | Description |
|---------|-------------|
| OHLCV data input | Loading and normalizing OHLCV market data for signal generation |
| Data contract boundary | Future multi-source data contract definitions |
| Factor calculation | Executing paper-derived factor formulas |
| Signal composition | Converting factor outputs into signal artifact rows |
| signal.csv export | Exporting standardized signal DataFrame to CSV |
| signal_contract.yaml export | Exporting signal contract metadata to YAML |
| data_quality_report.json export | Exporting data quality report to JSON |
| AlphaForge-compatible signal schema validation | Pure schema validation for signal artifacts |

## SignalForge Does NOT Own

| Concern | Rationale |
|---------|-----------|
| Backtesting | Owned by AlphaForge or external backtesting system |
| Strategy search over performance metrics | Beyond signal generation scope |
| Final holdout evaluation | Validation concern |
| Portfolio construction | Downstream strategy layer |
| Live trading | Execution concern |
| Broker execution | Execution concern |
| AlphaForge report generation | AlphaForge owns its own reporting |

## Interface Points

### Upstream Data Sources

SignalForge accepts OHLCV data from external data sources. The data contract boundary defines expected schema.

### Downstream Consumer: AlphaForge

AlphaForge consumes SignalForge artifacts through a custom_signal interface. SignalForge must not import AlphaForge in MVP unit tests.

### Explicit Exclusion

No import of AlphaForge in SignalForge MVP code. Compatibility is pure schema validation only.

## Constraints

- No backtest.py in MVP
- No performance metric ranking in MVP
- No portfolio logic in MVP
- No AlphaForge report generation in MVP
- No broker execution logic in MVP
