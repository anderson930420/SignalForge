# Tasks: Implement Runnable MVP Pipeline

## Task 1: Create CLI Entry Point

**File:** `src/signalforge/cli.py`

**Steps:**
1. Create `src/signalforge/cli.py` with `typer` app
2. Create `generate` subcommand with `--config` and `--overwrite` options
3. Add `signalforge` console script entry point to `pyproject.toml`

**Verification:**
- `signalforge --help` shows `generate` command

## Task 2: Implement Config Loading

**File:** `src/signalforge/cli.py`

**Steps:**
1. Load YAML config using `PyYAML`
2. Validate required fields: signal_name, source, factor_name, data_source, datetime_range, output
3. Add error handling for missing/invalid fields
4. Print error and exit with code 1 on validation failure

**Verification:**
- Missing required field produces clear error message

## Task 3: Register Built-in Factors

**File:** `src/signalforge/cli.py` (in `generate` command)

**Steps:**
1. Create FactorRegistry instance
2. Register MoskowitzMomentumFactor with name "moskowitz_momentum"
3. Use FactorRegistry.get() to resolve factor from config

**Verification:**
- Unknown factor name produces clear error: "Unknown factor: {name}"

## Task 4: Load OHLCV Data

**File:** `src/signalforge/cli.py` (in `generate` command)

**Steps:**
1. Use DataRegistry.local_ohlcv_csv() with path and symbol from config
2. Filter data by datetime_range if configured
3. Handle MissingColumnsError with clear message

**Verification:**
- Invalid CSV path produces clear error message

## Task 5: Compute Factor

**File:** `src/signalforge/cli.py` (in `generate` command)

**Steps:**
1. Call factor.calculate(data) with loaded OHLCV DataFrame
2. Handle edge cases (insufficient data, null values)

**Verification:**
- Factor output contains 'factor_value' column

## Task 6: Compose Signal

**File:** `src/signalforge/cli.py` (in `generate` command)

**Steps:**
1. Create SignalComposer instance with SignalValidator
2. Compose signal with: datetime, available_at, symbol, signal_name, source
3. Use signal_binary rule: 1 if signal_value > 0 else 0

**Verification:**
- Output contains all 7 required columns in stable order

## Task 7: Export Artifacts

**File:** `src/signalforge/cli.py` (in `generate` command)

**Steps:**
1. Build output directory path: `{artifacts_dir}/{symbol}/{start}_{end}/`
2. Check for existing files (if not --overwrite)
3. Use build_signal_contract() and build_data_quality_report() helpers
4. Export signal.csv, signal_contract.yaml, data_quality_report.json

**Verification:**
- All three files created in correct directory structure
- Files overwritten when --overwrite is set

## Task 8: Print Success Output

**File:** `src/signalforge/cli.py` (in `generate` command)

**Steps:**
1. Print artifact paths to stdout on success
2. Use format:
   ```
   Signal artifacts generated successfully:
     - {output_dir}/signal.csv
     - {output_dir}/signal_contract.yaml
     - {output_dir}/data_quality_report.json
   ```

**Verification:**
- Success output matches required format

## Task 9: Add Console Script Entry Point

**File:** `pyproject.toml`

**Steps:**
1. Add `signalforge = "signalforge.cli:app"` to `[project.scripts]` section

**Verification:**
- `signalforge generate --help` works after pip install -e .

## Task 10: Update Tests

**Files:** `tests/test_cli.py` (new)

**Steps:**
1. Add tests for config parsing
2. Add tests for overwrite behavior
3. Add tests for error handling
4. Add integration test for full pipeline

**Verification:**
- All new tests pass
- Total test count increases from 52 to ~60+