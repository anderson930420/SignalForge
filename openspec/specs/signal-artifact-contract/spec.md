# Signal Artifact Contract

## Purpose

Define the canonical schema for signal.csv artifacts produced by SignalForge.

## Owner

SignalForge

## Requirements

### Requirement: Signal CSV Schema

SignalForge SHALL export signal artifacts as CSV with the following required columns in stable order:
1. datetime
2. available_at
3. symbol
4. signal_name
5. signal_value
6. signal_binary
7. source

#### Scenario: Column Order Stability
- **WHEN** signal.csv is exported
- **THEN** Columns SHALL appear in the specified order

### Requirement: Column Constraints

The signal artifact columns SHALL have the following constraints:

| Column | Constraint |
|--------|-------------|
| datetime | NOT NULL, ISO 8601 timestamp |
| available_at | NOT NULL, MUST be <= datetime |
| symbol | NOT NULL, string |
| signal_name | NOT NULL, string |
| signal_value | MAY BE NULL, float |
| signal_binary | NOT NULL, only 0 or 1 |
| source | NOT NULL, string |

#### Scenario: Temporal Constraint
- **WHEN** a signal row is created
- **THEN** available_at SHALL be <= datetime

#### Scenario: Binary Signal Constraint
- **WHEN** signal_binary is set
- **THEN** It SHALL contain only values 0 or 1

### Requirement: Uniqueness Constraint

SignalForge SHALL NOT allow duplicate (datetime, symbol, signal_name) rows.

#### Scenario: Duplicate Detection
- **WHEN** A signal would create a duplicate row
- **THEN** SignalForge SHALL raise a validation error

### Requirement: Nullability

The following columns SHALL NOT be NULL: datetime, available_at, symbol, signal_name, signal_binary, source. The signal_value column MAY be NULL.

#### Scenario: Null Detection
- **WHEN** A required column contains NULL
- **THEN** SignalForge SHALL raise a validation error

### Requirement: AlphaForge Compatibility

The signal artifact schema SHALL be compatible with AlphaForge custom_signal interface.

#### Scenario: Schema Compatibility
- **WHEN** AlphaForge consumes signal.csv
- **THEN** It SHALL be able to parse all columns correctly
