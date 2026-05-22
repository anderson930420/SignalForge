# Proposal: Harden Canonical Signal Contract Validators

## Change Name

harden-canonical-signal-contract-validators

## What

Update the pure compatibility validators so `signal_contract.yaml` validation matches the canonical nested SignalForge v0.1 schema.

## Why

The export pipeline now writes canonical nested contract metadata, but the compatibility helper still checks legacy fields such as `exported_at`, `generator`, `signals`, and `compatibility`. This makes the validator disagree with the generated artifact contract.

## User Impact

Users and downstream checks can validate current SignalForge artifacts without requiring legacy timestamp or signal-list fields.

## Scope

### In Scope

- Canonical nested `signal_contract.yaml` schema validation.
- Lightweight `signal.csv` to contract consistency checks using `output.columns`, `signal_name`, and `source`.
- Regression tests for canonical pass and key failure cases.

### Out of Scope

- `signal.csv` schema changes.
- Artifact export behavior changes.
- Volatile timestamp fields.
- AlphaForge imports.
- Backtesting, performance ranking, or portfolio logic.
