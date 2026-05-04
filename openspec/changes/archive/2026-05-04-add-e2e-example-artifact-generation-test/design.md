# Design: End-to-End Example Artifact Generation Test

## Overview

This change adds a real end-to-end pytest that exercises the full CLI pipeline from YAML config to generated artifacts.

## Public Contracts Affected

**No public contracts change.** This is pure test coverage for:
- cli-generate-contract (existing CLI pipeline)
- signal-export-contract (existing artifact generation)

No new specs or delta specs required.

## Test File Location

`tests/test_e2e_generate_artifacts.py`

## Test Structure

### 1. Mock Data Generation

Generate deterministic OHLCV CSV with:
- 300 business day rows (enough for lookback=252, skip=21)
- Sequential dates with realistic price movements
- Columns: datetime, open, high, low, close, volume

### 2. Config Generation

Create YAML config with:
```yaml
signal_name: moskowitz_momentum
source: moskowitz_2024
factor_name: moskowitz_momentum
factor_params: {}
data_source:
  type: local_ohlcv_csv
  path: <generated_csv_path>
  symbol: AAPL
datetime_range:
  start: "2023-01-01"
  end: "2024-12-31"
output:
  artifacts_dir: <tmp_path>/artifacts
```

### 3. CLI Invocation

Use Typer CliRunner to invoke:
```
signalforge generate --config <config_path> --overwrite
```

### 4. Artifact Assertions

#### signal.csv
- 7 columns in stable order: datetime, available_at, symbol, signal_name, signal_value, signal_binary, source
- Not empty
- signal_binary contains only 0 or 1
- available_at <= datetime
- No duplicate (datetime, symbol, signal_name) rows

#### signal_contract.yaml
- signal_name exists
- factor name exists
- decision_rule exists
- schema_version exists
- output_file == "signal.csv"

#### data_quality_report.json
- source_type == "csv"
- row_count > 0
- symbol_count == 1
- start_date exists
- end_date exists
- duplicate_rows exists
- missing_values exists
- warnings exists

### 5. Output Path

Assert: `{artifacts_dir}/AAPL/20230101_20241231/`

### 6. Cleanup

Use pytest tmp_path fixture for automatic cleanup. Do not commit artifacts.

## Key Implementation Notes

- Use `pd.bdate_range` for business day generation
- Generate realistic price movements to avoid edge cases
- Ensure first datetime is early enough for 252-day lookback
- Use CliRunner to invoke the app (not the command directly)
- Check Typer version compatibility for CliRunner usage

## Testing Approach

- Single integration test with comprehensive assertions
- No fixtures needed beyond tmp_path
- Deterministic mock data ensures reproducibility