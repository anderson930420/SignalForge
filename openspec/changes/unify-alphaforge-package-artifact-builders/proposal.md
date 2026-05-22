# Proposal: Unify AlphaForge Package Artifact Builders

## Change Name

unify-alphaforge-package-artifact-builders

## What

Update the AlphaForge compatibility package export helper to build `signal_contract.yaml` and `data_quality_report.json` through the same canonical builders used by the main SignalForge generation path.

## Why

The compatibility package helper still emits older flat metadata schemas. That creates a second artifact contract inside SignalForge and can drift from the canonical CLI-generated artifacts.

## Scope

### In Scope

- Reuse `build_signal_contract()` for package `signal_contract.yaml`
- Reuse `build_market_data_quality_report()` for package `data_quality_report.json`
- Update package self-validation for canonical nested schema keys
- Update package regression tests

### Out of Scope

- CLI artifact schema changes
- AlphaForge imports
- Backtesting
- Performance metrics
- Package file-list changes
