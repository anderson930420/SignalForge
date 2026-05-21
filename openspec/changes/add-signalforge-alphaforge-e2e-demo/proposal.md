# Proposal: Add SignalForge-to-AlphaForge E2E Demo

## Change Name

add-signalforge-alphaforge-e2e-demo

## What

Add a reproducible demo that generates real SignalForge artifacts and feeds the generated `signal.csv` into AlphaForge's `custom_signal` research-validation workflow.

## Why

SignalForge v0.1 and AlphaForge custom-signal readiness are independently green. The next proof point is a real file-based handoff using SignalForge-generated artifacts rather than hand-written AlphaForge fixtures.

## User Impact

Users can run one documented demo flow to see:

- SignalForge generate a canonical artifact package from deterministic OHLCV data.
- AlphaForge consume the generated `signal.csv` through `custom_signal`.
- AlphaForge validate target-position mapping, missing-date behavior, extra-date rejection, and the no-runtime-import boundary.
- Both projects remain within their ownership boundaries.

## Scope

### In Scope

- Demo runbook documentation.
- Optional local automation for the cross-repo demo.
- Deterministic OHLCV input generation for the demo.
- Validation evidence from SignalForge and AlphaForge commands.

### Out of Scope

- New factor families.
- Signal artifact schema changes.
- AlphaForge execution-law changes.
- SignalForge imports from AlphaForge.
- AlphaForge imports from SignalForge runtime.
- Backtesting, portfolio construction, live trading, or broker execution inside SignalForge.
