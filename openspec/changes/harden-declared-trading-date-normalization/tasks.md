# Tasks

## 1. OpenSpec

- [x] Add narrow spec deltas for declared trading-date compatibility normalization.

## 2. Implementation

- [x] Add reusable declared daily trading-date normalization helper.
- [x] Update `validate_signal_market_date_alignment()` to compare declared daily dates.
- [x] Update AlphaForge compatibility package normalization and readback validation to use declared daily dates.
- [x] Preserve deterministic package files and existing schemas.

## 3. Tests

- [x] Cover offset timestamp alignment for `+08:00`, `Z`, and intraday offset strings.
- [x] Cover declared-date mismatch failures.
- [x] Cover package output preserving declared trading dates for offset timestamps.
- [x] Cover `available_at` same declared date passing and later declared date failing.
- [x] Cover clear invalid datetime validation errors.

## 4. Validation

- [x] Run `python3 -m pytest`.
- [x] Run `ruff check .`.
- [x] Run `openspec validate --all --strict`.

Validation evidence:

- Focused `python3 -m pytest tests/test_alphaforge_compatibility.py tests/test_alphaforge_compatibility_package_builder.py`: 32 passed.
- `openspec validate harden-declared-trading-date-normalization --strict`: passed.
- Initial full `python3 -m pytest`: 138 passed.
- Initial `ruff check .`: passed.
- Initial `openspec validate --all --strict`: 23 passed.
