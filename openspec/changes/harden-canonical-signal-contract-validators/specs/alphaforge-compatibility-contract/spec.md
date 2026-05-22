# AlphaForge Compatibility Contract

## MODIFIED Requirements

### Requirement: signal_contract.yaml Validation

The validation SHALL verify the canonical nested `signal_contract.yaml` schema without importing AlphaForge.

#### Scenario: Canonical contract accepted

- **WHEN** a contract contains the canonical nested schema
- **THEN** validation succeeds

#### Scenario: Legacy fields not required

- **WHEN** a contract omits `exported_at`, `generator`, and the legacy `signals` list
- **THEN** validation does not fail because of those omitted fields

### Requirement: Cross-Artifact Validation

The validation SHALL verify lightweight consistency between `signal.csv` and `signal_contract.yaml`.

#### Scenario: Signal columns match contract

- **WHEN** `signal.csv` columns differ from `contract.output.columns`
- **THEN** validation fails

#### Scenario: Signal name matches contract

- **WHEN** `signal.csv` contains a `signal_name` different from `contract.signal_name`
- **THEN** validation fails

#### Scenario: Source matches contract

- **WHEN** `signal.csv` contains a `source` different from `contract.source`
- **THEN** validation fails
