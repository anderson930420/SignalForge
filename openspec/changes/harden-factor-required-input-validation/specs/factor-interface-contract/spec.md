# Factor Interface Contract

## ADDED Requirements

### Requirement: Reusable Required Input Validation

Factor input validation SHALL be available as a reusable helper for factor implementations.

#### Scenario: Missing required factor input columns

- **WHEN** required factor input columns are missing from the input DataFrame
- **THEN** validation raises `ValueError`
- **AND** the error message identifies the factor name
- **AND** the error message lists the missing column names

#### Scenario: Present required factor input columns

- **WHEN** all required factor input columns are present in the input DataFrame
- **THEN** validation succeeds without modifying the input DataFrame
