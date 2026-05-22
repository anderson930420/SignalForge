# Tasks: Document Daily Datetime Contract

## Task 1: Specify the daily datetime policy

Status: Complete

**Files:** `openspec/changes/document-daily-datetime-contract/specs/*/spec.md`

**Steps:**
1. Define `datetime` and `available_at` as daily trading-date labels for MVP OHLCV signals.
2. Define no UTC-shifted-instant alignment for daily signals.
3. Define no intraday event-time validation claim.

## Task 2: Update producer-facing docs

Status: Complete

**Files:** `README.md`, `docs/alphaforge_handoff.md`, `docs/demos/signalforge_to_alphaforge_e2e.md`

**Steps:**
1. Document daily trading-date label semantics in the README.
2. Add handoff policy text for AlphaForge daily date alignment.
3. Add demo limitation text for intraday timing semantics.

## Task 3: Update deterministic timing-rule text

Status: Complete

**Files:** `src/signalforge/cli.py`, `src/signalforge/export.py`, tests

**Steps:**
1. Emit a clearer `timing.available_at_rule` for OHLCV-only daily signals.
2. Preserve the existing signal contract YAML schema shape.
3. Update deterministic expectations.

## Task 4: Validate

Status: Complete

**Commands:**
1. `python3 -m pytest`
2. `ruff check .`
3. `openspec validate --all --strict`

**Focused result:** `python3 -m pytest tests/test_readme.py tests/test_demo_docs.py tests/test_export.py tests/test_cli.py tests/test_e2e_generate_artifacts.py tests/test_alphaforge_compatibility.py tests/test_alphaforge_compatibility_package_builder.py` passed with 54 tests; `openspec validate document-daily-datetime-contract --strict` passed.
