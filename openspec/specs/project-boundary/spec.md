# Project Boundary

## Purpose

Define the ownership boundary of SignalForge MVP, excluding concerns owned by other systems.

## Owner

SignalForge
## Requirements
### Requirement: SignalForge Ownership Scope

SignalForge SHALL own the following concerns:
- OHLCV data input for signal generation
- Future multi-source data contract boundaries
- Factor calculation
- Signal composition
- signal.csv export
- signal_contract.yaml export
- data_quality_report.json export
- AlphaForge-compatible signal schema validation

#### Scenario: OHLCV Data Input
- **WHEN** SignalForge loads market data
- **THEN** It SHALL normalize and validate OHLCV columns

#### Scenario: Factor Calculation
- **WHEN** A factor is executed
- **THEN** SignalForge SHALL produce standardized signal artifacts

#### Scenario: Artifact Export
- **WHEN** SignalForge exports signals
- **THEN** It SHALL produce signal.csv, signal_contract.yaml, and data_quality_report.json

### Requirement: SignalForge Exclusion Scope

SignalForge SHALL NOT own the following concerns:
- Backtesting
- Strategy search over performance metrics
- Final holdout evaluation
- Portfolio construction
- Live trading
- Broker execution
- AlphaForge report generation

#### Scenario: No Backtesting
- **WHEN** SignalForge is executing
- **THEN** It SHALL NOT run any backtesting logic

#### Scenario: No AlphaForge Import
- **WHEN** SignalForge MVP unit tests run
- **THEN** They SHALL NOT import AlphaForge

### Requirement: AlphaForge Boundary

SignalForge SHALL be able to export signal.csv artifacts that AlphaForge can consume through a custom_signal interface.

#### Scenario: AlphaForge Compatibility
- **WHEN** AlphaForge consumes SignalForge artifacts
- **THEN** The schema SHALL be compatible with AlphaForge custom_signal interface

### Requirement: MVP Constraints

SignalForge MVP SHALL NOT include backtest.py, performance metric ranking, portfolio logic, AlphaForge report generation, or broker execution logic.

#### Scenario: MVP Exclusions
- **WHEN** MVP implementation decisions are made
- **THEN** The implementation SHALL NOT include excluded features

### Requirement: Smoke Export Boundary

The AlphaForge compatibility smoke export package SHALL be produced without importing AlphaForge and SHALL NOT add AlphaForge as a SignalForge dependency.

#### Scenario: No AlphaForge Runtime Coupling
- **WHEN** the smoke export package is defined or later implemented
- **THEN** SignalForge SHALL remain isolated from AlphaForge internals and dependencies

