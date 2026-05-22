# Proposal: Harden Factor Required Input Validation

## Change Name

harden-factor-required-input-validation

## What

Add a reusable factor input-column validator and apply it to `MoskowitzMomentumFactor.compute()`.

## Why

`MoskowitzMomentumFactor.required_inputs()` declares required columns, but `compute()` currently handles missing inputs inconsistently. Missing `close` silently returns a placeholder row, while missing `datetime` or `symbol` fails less clearly. Factor compute paths should fail before calculation with a clear, reusable error.

## User Impact

Users receive deterministic `ValueError` messages for missing factor inputs instead of placeholder factor outputs.

## Scope

### In Scope

- Reusable factor input-column validation in `factor_base.py`.
- `MoskowitzMomentumFactor.required_inputs()` includes `datetime`, `close`, and `symbol`.
- `MoskowitzMomentumFactor.compute()` raises a clear `ValueError` for missing required inputs.
- Regression tests for missing `close`, `datetime`, and `symbol`.
- Canonical factor output columns remain unchanged for valid input.

### Out of Scope

- `signal.csv` schema changes.
- SignalComposer behavior changes.
- New factors.
- AlphaForge imports.
- Backtesting, performance ranking, or portfolio logic.
- Legacy `calculate()` behavior changes.
