# CLI Generate Contract

## ADDED Requirements

### Requirement: Command Interface

The CLI SHALL provide a `generate` subcommand with the following interface:

```bash
signalforge generate --config <path> [--overwrite]
```

#### Scenario: Basic Command Invocation
- **WHEN** User runs `signalforge generate --config config.yaml`
- **THEN** The CLI SHALL parse the config file and execute the signal generation pipeline

### Requirement: Config File Contract

The config file SHALL be YAML format with the following required fields:

```yaml
signal_name: string        # Name of the signal
source: string            # Source identifier
factor_name: string       # Factor to use (must match FactorRegistry name)
factor_params: dict        # Factor-specific parameters
data_source:
  type: "local_ohlcv_csv"   # MVP supports only local CSV
  path: string            # Path to CSV file
  symbol: string | null   # Symbol to inject (if not in CSV)
datetime_range:
  start: string           # ISO 8601 start date
  end: string             # ISO 8601 end date
output:
  artifacts_dir: string  # Base output directory
```

#### Scenario: Config File Parsing
- **WHEN** Config file is provided
- **THEN** All required fields SHALL be present and valid

#### Scenario: Missing Config Fields
- **WHEN** Config file is missing required fields
- **THEN** The CLI SHALL exit with error and message indicating missing fields

### Requirement: Config Field Constraints

All config field constraints SHALL be enforced during validation.

#### Scenario: signal_name Constraint
- **WHEN** signal_name is validated
- **THEN** It SHALL NOT be empty

#### Scenario: source Constraint
- **WHEN** source is validated
- **THEN** It SHALL NOT be empty

#### Scenario: factor_name Constraint
- **WHEN** factor_name is validated
- **THEN** It SHALL match a registered factor name

#### Scenario: data_source.type Constraint
- **WHEN** data_source.type is validated
- **THEN** It SHALL be "local_ohlcv_csv" in MVP

#### Scenario: data_source.path Constraint
- **WHEN** data_source.path is validated
- **THEN** It SHALL be a valid file path

#### Scenario: datetime_range Constraints
- **WHEN** datetime_range is validated
- **THEN** start SHALL be before end and end SHALL be after start

### Requirement: Overwrite Behavior

The CLI SHALL NOT overwrite existing output files unless `--overwrite` flag is provided.

#### Scenario: Files Exist Without Overwrite
- **WHEN** Output files exist and `--overwrite` is NOT provided
- **THEN** The CLI SHALL exit with error: "Output files exist. Use --overwrite to replace."

#### Scenario: Files Exist With Overwrite
- **WHEN** Output files exist and `--overwrite` IS provided
- **THEN** The CLI SHALL replace existing files

### Requirement: Required Artifacts

The CLI SHALL produce exactly three artifacts in the output directory:

| Artifact | Format | Filename |
|----------|--------|----------|
| Signal data | CSV | signal.csv |
| Signal contract | YAML | signal_contract.yaml |
| Data quality report | JSON | data_quality_report.json |

#### Scenario: All Artifacts Produced
- **WHEN** Pipeline completes successfully
- **THEN** All three artifact files SHALL exist in the output directory

### Requirement: Output Path Structure

Artifacts SHALL be written to:
```
{artifacts_dir}/{symbol}/{datetime_range_start}_{datetime_range_end}/
```

#### Scenario: Path Determinism
- **WHEN** Same config is run twice
- **THEN** Output path SHALL be identical

### Requirement: Success Output

On successful completion, the CLI SHALL print:
```
Signal artifacts generated successfully:
  - {output_dir}/signal.csv
  - {output_dir}/signal_contract.yaml
  - {output_dir}/data_quality_report.json
```

#### Scenario: Success Output Format
- **WHEN** Pipeline completes successfully
- **THEN** The CLI SHALL print the artifact paths to stdout

### Requirement: Error Handling

The CLI SHALL exit with non-zero code and print error message on failure.

#### Scenario: Data Loading Failure
- **WHEN** CSV file cannot be loaded
- **THEN** CLI SHALL exit with error and message

#### Scenario: Factor Not Found
- **WHEN** factor_name is not registered
- **THEN** CLI SHALL exit with error: "Unknown factor: {name}"

### Requirement: Forbidden Behavior

The CLI SHALL NOT:
- Run backtests
- Compute performance metrics (Sharpe, drawdown, CAGR, etc.)
- Import AlphaForge runtime
- Add portfolio logic
- Perform strategy search
- Execute live trading

#### Scenario: No Backtest Execution
- **WHEN** `generate` command runs
- **THEN** It SHALL NOT execute any backtesting logic

### Requirement: MVP Scope

The CLI MVP SHALL support local CSV file loading, Moskowitz Momentum Factor, and single-symbol signal generation.

#### Scenario: MVP Supported Features
- **WHEN** MVP is running
- **THEN** It SHALL support local CSV file loading

#### Scenario: MVP Factor Support
- **WHEN** MVP is running
- **THEN** It SHALL support Moskowitz Momentum Factor

### Requirement: Future Scope (Non-MVP)

The CLI MVP SHALL NOT support multi-symbol generation in single run, database data sources, real-time data streams, or custom factor registration via CLI.

#### Scenario: No Multi-Symbol Support
- **WHEN** MVP is running
- **THEN** It SHALL NOT support multi-symbol generation in single run

#### Scenario: No Database Support
- **WHEN** MVP is running
- **THEN** It SHALL NOT support database data sources

#### Scenario: No Real-Time Support
- **WHEN** MVP is running
- **THEN** It SHALL NOT support real-time data streams

#### Scenario: No Custom Factor Registration
- **WHEN** MVP is running
- **THEN** It SHALL NOT support custom factor registration via CLI