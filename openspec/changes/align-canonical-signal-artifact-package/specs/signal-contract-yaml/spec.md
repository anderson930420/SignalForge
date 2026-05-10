# Signal Contract YAML

## Purpose

Define the canonical metadata structure for `signal_contract.yaml`.

## ADDED Requirements

### Requirement: Compatibility Block

The `signal_contract.yaml` SHALL include a `compatibility` block with:

- `alphaforge_strategy: custom_signal`
- `execution_semantics: legacy_close_to_close_lagged`
- `target_position_rule: "target_position = float(signal_binary)"`
- `supports_shorting: false`
- `supports_leverage: false`

#### Scenario: Compatibility Metadata
- **WHEN** the contract is generated
- **THEN** the compatibility block SHALL be present

### Requirement: Contract Provenance

The contract SHALL include canonical signal provenance, frequency, and schema information.

#### Scenario: Provenance Metadata
- **WHEN** signal_contract.yaml is created
- **THEN** it SHALL include signal_name, source, version, symbol, frequency, input_data, signal_schema, factor, and decision_rule

### Requirement: Co-location

The signal_contract.yaml SHALL be co-located with signal.csv in the artifacts directory.

#### Scenario: Artifact Co-location
- **WHEN** artifacts are exported
- **THEN** signal_contract.yaml SHALL be in the same directory as signal.csv
