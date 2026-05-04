# Proposal: AlphaForge Compatibility Smoke Export Package

## Change Name

add-alphaforge-compatibility-smoke-export

## What

Add a committed smoke export package under `examples/alphaforge_compatibility/AAPL_20230101_20241231/` that demonstrates SignalForge can emit AlphaForge-consumable artifacts without importing AlphaForge internals.

## Why

SignalForge needs a concrete, reviewable artifact bundle that proves the handoff boundary to AlphaForge. The package should document the exact files, schema expectations, and execution semantics needed for AlphaForge `custom_signal` consumption while keeping SignalForge isolated from AlphaForge dependencies.

## User Impact

Users and reviewers can inspect a deterministic example package containing market data, signals, contract metadata, quality reporting, and package documentation. The package serves as compatibility evidence for AlphaForge validation and backtesting workflows.

## Scope

### In Scope

- Example package layout under `examples/alphaforge_compatibility/AAPL_20230101_20241231/`
- Package-level contract for `market_data.csv`, `signal.csv`, `signal_contract.yaml`, `data_quality_report.json`, `manifest.json`, and `README.md`
- Explicit AlphaForge boundary requirements
- Deterministic compatibility semantics for the smoke package

### Out of Scope

- Runtime export implementation
- Export helper changes
- Test changes
- AlphaForge dependency additions
- AlphaForge runtime execution inside SignalForge

## Spec Areas Affected

- New `alphaforge-compatibility-smoke-export` package contract
- `signal-export-contract` boundary for the example package layout
- `project-boundary` explicit no-AlphaForge-import constraint

## Next Step

Proceed to design and spec deltas, then validate the change without touching runtime code or tests.
