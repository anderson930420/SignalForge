# AlphaForge Compatibility Contract

## Purpose

Define pure schema validation checks for AlphaForge-compatible signal artifacts.

## Owner

SignalForge

## Requirements

### Requirement: Compatibility Scope

SignalForge SHALL provide schema validation that AlphaForge can rely on without importing AlphaForge. This SHALL be pure Python validation.

#### Scenario: Pure Python Validation
- **WHEN** Compatibility checks are executed
- **THEN** They SHALL NOT import AlphaForge

### Requirement: signal.csv Validation

The validation SHALL verify: 7 columns, correct column order, ISO 8601 datetime format, binary values 0 or 1 only, available_at <= datetime, and NOT NULL constraints.

#### Scenario: Binary Value Validation
- **WHEN** signal_binary contains invalid values
- **THEN** Validation SHALL fail

#### Scenario: Temporal Constraint Validation
- **WHEN** available_at > datetime
- **THEN** Validation SHALL fail

### Requirement: Uniqueness Validation

The validation SHALL ensure no duplicate (datetime, symbol, signal_name) rows exist.

#### Scenario: Duplicate Row Detection
- **WHEN** Duplicate rows exist
- **THEN** Validation SHALL fail

### Requirement: signal_contract.yaml Validation

The validation SHALL verify: required top-level keys, generator = "SignalForge", non-empty signals list.

#### Scenario: Generator Value Validation
- **WHEN** generator is not "SignalForge"
- **THEN** Validation SHALL fail

#### Scenario: Empty Signals List Detection
- **WHEN** signals list is empty
- **THEN** Validation SHALL fail

### Requirement: Cross-Artifact Validation

The validation SHALL verify datetime_range alignment between contract and data.

#### Scenario: Datetime Range Alignment
- **WHEN** Contract datetime_range does not match data
- **THEN** Validation SHALL fail

### Requirement: Error Reporting

Validation errors SHALL include the check that failed, the artifact name, and affected row or field.

#### Scenario: Error Detail Completeness
- **WHEN** Validation fails
- **THEN** Error SHALL include specific check, artifact, and location
