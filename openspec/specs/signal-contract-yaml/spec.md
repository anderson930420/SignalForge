# Signal Contract YAML

## Purpose

Define the schema and structure of signal_contract.yaml artifacts exported by SignalForge.

## Owner

SignalForge

## Requirements

### Requirement: Contract YAML Schema

The signal_contract.yaml SHALL contain:
- version: string (Contract version)
- exported_at: ISO 8601 timestamp (When generated)
- generator: string (SHALL be "SignalForge")
- signals: list[SignalEntry] (SHALL be non-empty)

#### Scenario: Required Top-Level Keys
- **WHEN** signal_contract.yaml is created
- **THEN** It SHALL include version, exported_at, generator, and signals

### Requirement: SignalEntry Schema

Each SignalEntry SHALL contain:
- signal_name: string
- source: string
- symbols: list[string]
- datetime_range: {start: ISO 8601, end: ISO 8601}
- row_count: integer
- signal_value_stats: {min, max, mean, null_count}
- signal_binary_stats: {value_0_count, value_1_count, null_count}

#### Scenario: SignalEntry Completeness
- **WHEN** A SignalEntry is created
- **THEN** It SHALL contain all required fields

### Requirement: Non-Empty Signals List

The signals list SHALL be non-empty.

#### Scenario: Non-Empty Validation
- **WHEN** signal_contract.yaml is validated
- **THEN** signals SHALL contain at least one entry

### Requirement: Datetime Range Validity

When datetime_range is specified, start SHALL be <= end.

#### Scenario: Datetime Range Validation
- **WHEN** datetime_range is specified
- **THEN** start SHALL be <= end

### Requirement: Binary Stats Consistency

The signal_binary_stats SHALL be consistent: value_0_count + value_1_count + null_count SHALL equal row_count.

#### Scenario: Binary Stats Calculation
- **WHEN** signal_binary_stats are calculated
- **THEN** The sum SHALL equal row_count

### Requirement: Co-location

The signal_contract.yaml SHALL be co-located with signal.csv in the artifacts directory.

#### Scenario: Artifact Co-location
- **WHEN** artifacts are exported
- **THEN** signal_contract.yaml SHALL be in the same directory as signal.csv
