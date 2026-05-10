# CLI Generate Contract

## Purpose

Define the CLI output path and generation behavior for canonical signal artifacts.

## ADDED Requirements

### Requirement: Output Path Structure

The CLI SHALL write artifacts to:

`{artifacts_dir}/{symbol}/{signal_name}/{start_date}_{end_date}/`

#### Scenario: Path Determinism
- **WHEN** the same config is run twice
- **THEN** the output path SHALL be identical

### Requirement: Row-Level Export

The CLI SHALL export one signal row per selected OHLCV market-data row.

#### Scenario: Daily Output
- **WHEN** generate completes successfully
- **THEN** signal.csv SHALL contain the same number of rows as the selected OHLCV data

### Requirement: Validation

The CLI SHALL fail when signal dates do not match the selected OHLCV market dates.

#### Scenario: Missing Dates
- **WHEN** signal rows are missing for selected market dates
- **THEN** the CLI SHALL exit with an error
