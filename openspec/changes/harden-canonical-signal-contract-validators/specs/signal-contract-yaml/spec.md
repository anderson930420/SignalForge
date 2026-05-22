# Signal Contract YAML Specification

## MODIFIED Requirements

### Requirement: Contract YAML Schema

The `signal_contract.yaml` SHALL validate against the canonical nested SignalForge v0.1 schema.

The contract SHALL contain these top-level keys:

- `signal_name`
- `version`
- `source`
- `factor`
- `decision_rule`
- `data`
- `timing`
- `output`

The contract SHALL NOT require legacy `exported_at`, `generator`, or `signals` fields.

#### Scenario: Required top-level keys

- **WHEN** `signal_contract.yaml` is validated
- **THEN** it requires `signal_name`, `version`, `source`, `factor`, `decision_rule`, `data`, `timing`, and `output`
- **AND** it does not require `exported_at`
- **AND** it does not require `generator`
- **AND** it does not require a legacy `signals` list

#### Scenario: Required nested factor fields

- **WHEN** `signal_contract.yaml` is validated
- **THEN** `factor` contains `name`, `version`, and `parameters`

#### Scenario: Required decision rule fields

- **WHEN** `signal_contract.yaml` is validated
- **THEN** `decision_rule` contains `signal_binary`

#### Scenario: Required data fields

- **WHEN** `signal_contract.yaml` is validated
- **THEN** `data.required_columns` includes `datetime`, `open`, `high`, `low`, `close`, `volume`, and `symbol`

#### Scenario: Required timing fields

- **WHEN** `signal_contract.yaml` is validated
- **THEN** `timing.available_at_rule` exists

#### Scenario: Required output fields

- **WHEN** `signal_contract.yaml` is validated
- **THEN** `output.file` is `signal.csv`
- **AND** `output.schema_version` is `0.1.0`
- **AND** `output.columns` exactly equals `datetime`, `available_at`, `symbol`, `signal_name`, `signal_value`, `signal_binary`, `source`
