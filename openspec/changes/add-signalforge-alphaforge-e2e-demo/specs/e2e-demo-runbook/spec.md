# e2e-demo-runbook Specification

## ADDED Requirements

### Requirement: Reproducible SignalForge-to-AlphaForge demo

SignalForge SHALL provide a documented demo flow that generates real SignalForge artifacts from deterministic OHLCV input and then validates those artifacts through AlphaForge's `custom_signal` research-validation workflow.

#### Scenario: Demo generates and consumes real artifacts

- **GIVEN** the SignalForge repository and sibling AlphaForge repository are available locally
- **WHEN** the demo flow is run
- **THEN** SignalForge produces `signal.csv`, `signal_contract.yaml`, and `data_quality_report.json`
- **AND** AlphaForge consumes the generated `signal.csv` through `custom_signal`
- **AND** the demo records the generated AlphaForge output artifacts

#### Scenario: Demo preserves repository boundaries

- **GIVEN** AlphaForge consumes the generated `signal.csv`
- **WHEN** the custom-signal validation checks run
- **THEN** `signal_binary` maps to AlphaForge `target_position`
- **AND** missing signal dates default to flat positions
- **AND** extra signal dates fail validation
- **AND** AlphaForge does not import the SignalForge runtime
- **AND** `signal_value` is ignored for execution
