# Proposal: Add End-to-End Example Artifact Generation Test

## Change Name

add-e2e-example-artifact-generation-test

## What

Add a real end-to-end pytest that proves the runnable MVP pipeline can generate signal artifacts from a YAML config and local OHLCV CSV.

## Why

The CLI pipeline exists but lacks an integration test that proves the full pipeline works from config to artifact generation. This test will serve as a reproducible example and regression guard.

## User Impact

No external user impact. This is a developer-facing test.

## Scope

### In Scope

- Real end-to-end pytest using tmp_path
- Deterministic mock OHLCV CSV generation (300+ business day rows)
- YAML config using local_ohlcv_csv data source type
- CLI invocation via Typer CliRunner
- Assertions on all three artifact files
- Assertions on signal.csv schema and constraints
- Assertions on signal_contract.yaml fields
- Assertions on data_quality_report.json fields

### Out of Scope (Explicitly Forbidden)

- Real TWSE data
- backtest.py
- Performance metrics (Sharpe, CAGR, drawdown, etc.)
- AlphaForge runtime import
- Portfolio logic
- Committing generated artifacts

## Specs Affected

This is a test coverage addition for existing specs:
- cli-generate-contract (CLI pipeline)
- signal-export-contract (artifact generation)

No new specs or spec changes required. This is pure test coverage.

## Next Step

Proceed to design.md to outline the test structure.