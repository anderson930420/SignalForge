# alphaforge-compatibility-smoke-export Specification

## Purpose
TBD - created by archiving change add-alphaforge-compatibility-smoke-export. Update Purpose after archive.
## Requirements
### Requirement: Package Location

SignalForge SHALL define the smoke export package at:

`examples/alphaforge_compatibility/AAPL_20230101_20241231/`

The package SHALL contain exactly these files:

- `market_data.csv`
- `signal.csv`
- `signal_contract.yaml`
- `data_quality_report.json`
- `manifest.json`
- `README.md`

#### Scenario: Package Layout
- **WHEN** The smoke package is reviewed
- **THEN** The directory and file set SHALL match the required layout exactly

### Requirement: Market Data Contract

`market_data.csv` SHALL contain the following columns in order:

1. `datetime`
2. `open`
3. `high`
4. `low`
5. `close`
6. `volume`

The market data SHALL satisfy:

- The `datetime` set SHALL exactly match the `signal.csv` `datetime` set
- `open`, `high`, `low`, and `close` SHALL be finite and positive
- `high >= low`
- `high >= open`
- `high >= close`
- `low <= open`
- `low <= close`
- `volume` SHALL be present

#### Scenario: OHLC Integrity
- **WHEN** market data is prepared for the smoke package
- **THEN** OHLC values SHALL satisfy the integrity rules

### Requirement: Signal CSV Contract

`signal.csv` SHALL contain the stable column order:

1. `datetime`
2. `available_at`
3. `symbol`
4. `signal_name`
5. `signal_value`
6. `signal_binary`
7. `source`

The signal rows SHALL satisfy:

- `signal_binary` SHALL contain only `0` or `1`
- `available_at <= datetime`
- No duplicate `(datetime, symbol, signal_name)` rows SHALL exist
- `row_count` SHALL be greater than 1
- The `datetime` set SHALL exactly match the `market_data.csv` `datetime` set
- `signal_value` SHALL be present for provenance, but AlphaForge SHALL NOT use it for execution

#### Scenario: Signal Integrity
- **WHEN** the smoke package is consumed
- **THEN** the signal rows SHALL satisfy the stable schema and temporal rules

### Requirement: Signal Contract YAML

`signal_contract.yaml` SHALL include:

- `signal_name`
- `source`
- `factor`
- `factor_params`
- `decision_rule`
- `timing_rule`
- `schema_version`
- `output_file`
- `row_count`
- `symbol`
- `datetime_start`
- `datetime_end`
- `generator: SignalForge`

The `row_count` value SHALL refer to emitted signal rows.

#### Scenario: Contract Metadata Completeness
- **WHEN** the contract file is generated
- **THEN** all required provenance and timing fields SHALL be present

### Requirement: Data Quality Report

`data_quality_report.json` SHALL include:

- `source_type`
- `symbol_count`
- `row_count`
- `start_date`
- `end_date`
- `duplicate_rows`
- `missing_values`
- `warnings`
- `generator: SignalForge`

The `row_count` value SHALL refer to emitted signal rows for this smoke package.

#### Scenario: Quality Metadata Completeness
- **WHEN** the data quality report is generated
- **THEN** it SHALL expose the package-level quality summary fields

### Requirement: Manifest Contract

`manifest.json` SHALL include:

- `package_name`
- `package_version`
- `generator`
- `generated_for`
- `symbol`
- `start_date`
- `end_date`
- `market_data_file`
- `signal_file`
- `signal_contract_file`
- `data_quality_report_file`
- `row_count`
- `schema_version`
- `alpha_forge_strategy: custom_signal`
- `expected_alpha_forge_execution_semantics: legacy_close_to_close_lagged`

#### Scenario: Manifest Completeness
- **WHEN** the smoke package is inspected
- **THEN** the manifest SHALL describe the bundle and AlphaForge execution semantics

### Requirement: README Contract

`README.md` SHALL explain:

- what the package is
- that SignalForge generated the signal
- that AlphaForge validates and backtests it
- that AlphaForge must not import SignalForge internals
- the exact `alphaforge research-validate` command for consuming the package

#### Scenario: Package Documentation
- **WHEN** a reviewer opens the package README
- **THEN** the compatibility boundary and AlphaForge command SHALL be documented

### Requirement: Cross-Artifact Consistency

All artifacts in the smoke package SHALL agree on:

- `symbol`
- date range
- `row_count`
- generator identity

#### Scenario: Bundle Consistency
- **WHEN** the package is inspected as a whole
- **THEN** the contract, report, manifest, signal rows, and market data SHALL describe the same bundle

### Requirement: AlphaForge Boundary

SignalForge SHALL generate the smoke package without importing AlphaForge and without adding AlphaForge as a dependency.

#### Scenario: No AlphaForge Dependency
- **WHEN** the smoke package spec is implemented later
- **THEN** SignalForge SHALL remain AlphaForge-free

