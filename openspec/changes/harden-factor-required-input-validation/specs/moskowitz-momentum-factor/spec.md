# Moskowitz Momentum Factor

## MODIFIED Requirements

### Requirement: Required Input

The factor SHALL require `datetime`, `close`, and `symbol` columns for canonical `compute()` output.

#### Scenario: Missing close input

- **WHEN** `compute()` is called without the `close` column
- **THEN** it raises `ValueError`
- **AND** it does not return placeholder rows

#### Scenario: Missing datetime input

- **WHEN** `compute()` is called without the `datetime` column
- **THEN** it raises `ValueError`
- **AND** it does not return placeholder rows

#### Scenario: Missing symbol input

- **WHEN** `compute()` is called without the `symbol` column
- **THEN** it raises `ValueError`
- **AND** it does not return placeholder rows

#### Scenario: Valid canonical output

- **WHEN** `compute()` is called with `datetime`, `close`, and `symbol`
- **THEN** it returns the canonical factor output columns `datetime`, `symbol`, `factor_name`, `factor_value`, and `available_at`
