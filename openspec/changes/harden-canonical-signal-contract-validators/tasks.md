# Tasks: Harden Canonical Signal Contract Validators

## Task 1: Specify canonical validator behavior

Status: Complete

**Files:** `openspec/changes/harden-canonical-signal-contract-validators/specs/*/spec.md`

**Steps:**
1. Define canonical nested contract validation requirements.
2. Define lightweight cross-artifact consistency requirements.

## Task 2: Update compatibility validators

Status: Complete

**Files:** `src/signalforge/compatibility.py`

**Steps:**
1. Replace legacy contract key checks with canonical nested schema checks.
2. Validate `output.columns` against the stable `signal.csv` schema.
3. Validate cross-artifact columns, `signal_name`, and `source`.

## Task 3: Add regression tests

Status: Complete

**Files:** `tests/test_alphaforge_compatibility.py`

**Steps:**
1. Cover canonical contract pass behavior.
2. Cover missing nested required fields.
3. Cover wrong output columns.
4. Cover cross-artifact column and signal-name mismatches.

## Task 4: Validate

Status: Complete

**Commands:**
1. `python3 -m pytest`
2. `ruff check .`
3. `openspec validate --all --strict`

**Result:** Passed with 117 tests, ruff clean, and 19 OpenSpec items valid.
