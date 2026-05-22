# Tasks: Harden Factor Required Input Validation

## Task 1: Add reusable validator

**Files:** `src/signalforge/factor_base.py`

**Steps:**
1. [x] Add a helper that validates required input columns for a factor.
2. [x] Raise `ValueError` with the factor name and missing column names.

## Task 2: Apply to Moskowitz factor

**Files:** `src/signalforge/factors/moskowitz_momentum.py`

**Steps:**
1. [x] Include `datetime`, `close`, and `symbol` in `required_inputs()`.
2. [x] Call the shared validator at the start of `compute()`.
3. [x] Preserve canonical output columns for valid input.
4. [x] Preserve legacy `calculate()` behavior.

## Task 3: Update tests and validation

**Files:** `tests/test_factor_base.py`, `tests/test_moskowitz_momentum.py`

**Steps:**
1. [x] Add helper tests for clear missing-column errors.
2. [x] Add Moskowitz tests for missing `close`, `datetime`, and `symbol`.
3. [x] Confirm valid data still produces canonical factor output.
4. [x] Run `python3 -m pytest`.
5. [x] Run `ruff check .`.
6. [x] Run `openspec validate --all --strict`.
