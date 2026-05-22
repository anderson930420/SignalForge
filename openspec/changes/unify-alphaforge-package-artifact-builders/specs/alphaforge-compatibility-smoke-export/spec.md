# alphaforge-compatibility-smoke-export Specification

## MODIFIED Requirements

### Requirement: Signal Contract YAML

`signal_contract.yaml` SHALL use the canonical SignalForge signal contract builder schema.

The contract SHALL include:

- `signal_name`
- `version`
- `source`
- `factor`
- `decision_rule`
- `data`
- `timing`
- `output`

The `factor` value SHALL be an object containing:

- `name`
- `version`
- `parameters`

The `output.columns` value SHALL equal the canonical `signal.csv` columns:

1. `datetime`
2. `available_at`
3. `symbol`
4. `signal_name`
5. `signal_value`
6. `signal_binary`
7. `source`

#### Scenario: Contract Metadata Completeness
- **WHEN** the package contract file is generated
- **THEN** it SHALL use the canonical nested SignalForge contract schema

### Requirement: Data Quality Report

`data_quality_report.json` SHALL use the canonical market-data quality report builder schema.

The report SHALL include:

- `version`
- `generator`
- `dataset_name`
- `source_type`
- `symbol_count`
- `row_count`
- `start_date`
- `end_date`
- `duplicate_rows`
- `missing_values`
- `warnings`
- `point_in_time_correctness_claimed`

The `missing_values` value SHALL be an object keyed by OHLCV column:

- `open`
- `high`
- `low`
- `close`
- `volume`

The `point_in_time_correctness_claimed` value SHALL be `false`.

#### Scenario: Quality Metadata Completeness
- **WHEN** the package data quality report is generated
- **THEN** it SHALL use the canonical market-data quality report schema
