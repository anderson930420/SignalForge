# Signal Composer Contract

## Purpose

Define the signal composer that converts factor outputs into signal artifact rows.

## Owner

SignalForge

## Requirements

### Requirement: Composition Input

The composer SHALL accept factor output DataFrame, factor metadata, timestamp metadata, and symbol.

#### Scenario: Input Acceptance
- **WHEN** Valid inputs are provided
- **THEN** The composer SHALL accept and process them

### Requirement: Composition Output

The composer SHALL produce a DataFrame conforming to signal-artifact-contract schema.

#### Scenario: Output Conformance
- **WHEN** Composition completes
- **THEN** Output SHALL conform to signal-artifact-contract

### Requirement: Column Mapping

The composer SHALL map factor outputs to signal columns: datetime, available_at, symbol, signal_name, signal_value, signal_binary, source.

#### Scenario: Correct Column Mapping
- **WHEN** Composition occurs
- **THEN** All columns SHALL be mapped correctly

### Requirement: Binary Signal Derivation Rule

When signal_binary is not explicitly provided, signal_value > 0 SHALL result in signal_binary = 1, and signal_value <= 0 SHALL result in signal_binary = 0.

#### Scenario: Positive Value Derivation
- **WHEN** signal_value > 0 and no explicit signal_binary
- **THEN** signal_binary SHALL be 1

#### Scenario: Non-Positive Value Derivation
- **WHEN** signal_value <= 0 and no explicit signal_binary
- **THEN** signal_binary SHALL be 0

### Requirement: Data Preservation

The composer SHALL NOT modify factor output DataFrame and SHALL preserve all rows including null signal_values.

#### Scenario: Null Preservation
- **WHEN** signal_value is null
- **THEN** It SHALL be preserved, not filtered

### Requirement: Column Order Enforcement

The composer SHALL ensure column order matches signal-artifact-contract.

#### Scenario: Column Order Verification
- **WHEN** Output is produced
- **THEN** Column order SHALL match specification
