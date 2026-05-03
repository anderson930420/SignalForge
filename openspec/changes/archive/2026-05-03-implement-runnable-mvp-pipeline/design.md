# Design: Runnable MVP Pipeline

## Overview

The signal generation CLI is a thin orchestration layer that wires together existing components:

```
DataRegistry → FactorRegistry → Factor → SignalComposer → Export
```

## Component Architecture

```text
signalforge generate
├── config loading and validation (PyYAML)
├── DataRegistry.local_ohlcv_csv()
├── FactorRegistry.get_factor()
├── factor.compute()
├── SignalComposer.compose()
└── export required artifacts
```

## Implementation Location

- CLI entry point: `src/signalforge/cli.py`
- Optional orchestration module: `src/signalforge/pipeline.py`

## Public CLI Contract

### Command

```bash
signalforge generate --config <path> [--overwrite]
```

### Config Schema (YAML)

```yaml
signal_name: moskowitz_momentum
source: moskowitz_2024

factor_name: moskowitz_momentum
factor_params:
  lookback_days: 252
  skip_days: 21

data_source:
  type: local_ohlcv_csv
  path: /path/to/data.csv
  symbol: "2330"

datetime_range:
  start: "2023-01-01"
  end: "2024-12-31"

output:
  artifacts_dir: artifacts
```

## Output Structure

```
artifacts/
└── {symbol}/
    └── {start_date}_{end_date}/
        ├── signal.csv
        ├── signal_contract.yaml
        └── data_quality_report.json
```

## Success Output

After successful generation, the CLI SHALL print the generated artifact paths:

- signal.csv
- signal_contract.yaml
- data_quality_report.json

## Key Implementation Notes

### Config Loading

Use `PyYAML` to load config. Validate required fields before processing.

### Data Loading

Use `DataRegistry.local_ohlcv_csv(filepath, symbol)` to load OHLCV data.

### Factor Resolution

Use `FactorRegistry.get_factor(factor_name)` to get the factor. Register built-in factors at startup.

### Signal Composition

Use `SignalComposer().compose()` with factor output to produce signal artifact.

### Artifact Export

Use `export_signal_csv()`, `export_signal_contract_yaml()`, and `export_data_quality_report()` from `export.py`.

Use `build_signal_contract()` and `build_data_quality_report()` helper functions for constructing artifact data.

### Overwrite Check

Before exporting, check if files exist. If they exist and `--overwrite` is False, exit with error.

## Dependencies

- `typer` for CLI (already in requirements.txt)
- `PyYAML` for config parsing (already in requirements.txt)
- Existing SignalForge modules

## Testing Approach

- Unit test for config parsing
- Unit test for overwrite behavior
- Integration test for full pipeline (mock data)

## Non-Goals (Explicitly Excluded)

- No backtest execution
- No performance metrics
- No AlphaForge import
- No portfolio logic
- No strategy search