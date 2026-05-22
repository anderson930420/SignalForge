# Tasks: Unify AlphaForge Package Artifact Builders

## Task 1: Reuse canonical artifact builders

**Files:** `src/signalforge/export.py`

**Steps:**
1. [x] Build package `signal_contract.yaml` with `build_signal_contract()`.
2. [x] Build package `data_quality_report.json` with `build_market_data_quality_report()`.
3. [x] Preserve manifest and README behavior.
4. [x] Preserve `contains_backtest_results: false` and `contains_performance_metrics: false`.

## Task 2: Update package validation

**Files:** `src/signalforge/export.py`

**Steps:**
1. [x] Validate canonical nested signal contract keys.
2. [x] Validate canonical market-data quality report keys.
3. [x] Remove old flat schema expectations.

## Task 3: Update tests and validation

**Files:** `tests/test_alphaforge_compatibility_package_builder.py`

**Steps:**
1. [x] Assert canonical nested signal contract schema.
2. [x] Assert market-data quality report missing values are keyed by OHLCV column.
3. [x] Assert manifest boundary flags remain false.
4. [x] Run pytest, ruff, and OpenSpec validation.
