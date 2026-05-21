# Tasks: Add SignalForge-to-AlphaForge E2E Demo

## Task 1: Add reproducible demo assets

Status: Complete

**Files:** `scripts/run_signalforge_alphaforge_demo.py`

**Steps:**
1. Create deterministic OHLCV input for the demo.
2. Run the public SignalForge generate command.
3. Locate the generated `signal.csv`, `signal_contract.yaml`, and `data_quality_report.json`.
4. Invoke AlphaForge through its public `custom_signal` workflow.

## Task 2: Add demo documentation

Status: Complete

**Files:** `docs/demos/signalforge_to_alphaforge_e2e.md`

**Steps:**
1. Document purpose and prerequisites.
2. Document the SignalForge command and generated artifacts.
3. Document the AlphaForge command and generated artifacts.
4. Record validation results and boundary notes.
5. Document known limitations.

## Task 3: Add focused regression coverage

Status: Complete

**Files:** `tests/test_demo_docs.py`

**Steps:**
1. Verify the demo document exists.
2. Verify the document contains the required demo sections and boundary notes.
3. Verify the automation script exists.

## Task 4: Validate

Status: Complete

**Commands:**
1. `python3 -m pytest`
2. `ruff check .`
3. `openspec validate --all --strict`
