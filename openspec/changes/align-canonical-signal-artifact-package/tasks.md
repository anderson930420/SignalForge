# Tasks: Align Canonical Signal Artifact Package

## Task 1: Update CLI row-level signal generation

**Files:** `src/signalforge/cli.py`, `src/signalforge/signal_composer.py`

**Steps:**
1. Compose one signal row per selected OHLCV row.
2. Preserve warmup rows with `signal_value` allowed to be null.
3. Emit `signal_binary = 0` for warmup rows.
4. Validate that generated signal dates match selected market dates by default.

## Task 2: Update output path and contract metadata

**Files:** `src/signalforge/cli.py`, `src/signalforge/export.py`

**Steps:**
1. Change output layout to `{artifacts_dir}/{symbol}/{signal_name}/{start_date}_{end_date}/`.
2. Add compatibility metadata to `signal_contract.yaml`.
3. Keep `signal.csv`, `signal_contract.yaml`, and `data_quality_report.json` co-located.

## Task 3: Add or update tests

**Files:** `tests/test_cli.py`, `tests/test_e2e_generate_artifacts.py`, `tests/test_signal_artifact_contract.py`, `tests/test_alphaforge_compatibility.py`

**Steps:**
1. Verify row-level export length and stable column order.
2. Verify warmup row handling and date alignment.
3. Verify the updated output path.
4. Verify canonical compatibility metadata in the exported contract.

