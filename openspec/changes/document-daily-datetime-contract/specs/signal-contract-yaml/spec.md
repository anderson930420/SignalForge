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

For MVP daily OHLCV signals, `timing.available_at_rule` SHALL describe `available_at` as the same declared daily trading date as `datetime`.

#### Scenario: Required timing fields

- **WHEN** `signal_contract.yaml` is validated
- **THEN** `timing.available_at_rule` exists
- **AND** for OHLCV-only daily signals it states `same declared daily trading date as datetime for OHLCV-only daily signal`
