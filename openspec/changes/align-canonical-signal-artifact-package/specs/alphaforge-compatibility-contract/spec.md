# AlphaForge Compatibility Contract

## Purpose

Define pure schema validation checks for canonical SignalForge signal artifacts.

## ADDED Requirements

### Requirement: Compatibility Scope

SignalForge SHALL provide schema validation that AlphaForge can rely on without importing AlphaForge. This SHALL be pure Python validation.

#### Scenario: Pure Python Validation
- **WHEN** Compatibility checks are executed
- **THEN** They SHALL NOT import AlphaForge

### Requirement: signal.csv Validation

The validation SHALL verify: 7 columns, correct column order, binary values 0 or 1 only, available_at <= datetime, and NOT NULL constraints.

#### Scenario: Binary Value Validation
- **WHEN** signal_binary contains invalid values
- **THEN** Validation SHALL fail

#### Scenario: Temporal Constraint Validation
- **WHEN** available_at > datetime
- **THEN** Validation SHALL fail

### Requirement: Date Alignment Validation

The validation SHALL ensure signal dates equal the selected OHLCV market dates.

#### Scenario: Missing Signal Date Detection
- **WHEN** a selected market date has no signal row
- **THEN** Validation SHALL fail

### Requirement: signal_contract.yaml Validation

The validation SHALL verify required top-level metadata and canonical compatibility fields.

#### Scenario: Compatibility Block Validation
- **WHEN** compatibility metadata is missing
- **THEN** Validation SHALL fail
