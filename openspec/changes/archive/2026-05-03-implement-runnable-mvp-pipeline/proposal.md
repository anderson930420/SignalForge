# Proposal: Implement Runnable MVP Pipeline

## Change Name

implement-runnable-mvp-pipeline

## What

Add a minimal runnable CLI pipeline (`signalforge generate --config <yaml>`) that can produce signal artifacts from a YAML config file.

## Why

SignalForge currently has all building blocks (DataRegistry, FactorRegistry, SignalComposer, export functions) but they must be wired together manually in Python. A user-facing CLI enables non-programmatic use and reproducible artifact generation.

## User Impact

A user can run:
```bash
signalforge generate --config examples/twse_2330_moskowitz_signal.yaml
```

And receive:
- signal.csv
- signal_contract.yaml
- data_quality_report.json

In a deterministic output directory without writing Python code.

## Scope

### In Scope

- CLI entry point: `signalforge generate`
- YAML config file parsing
- DataRegistry loading from local CSV
- Factor resolution from FactorRegistry
- Factor computation
- SignalComposer signal assembly
- Artifact export (signal.csv, signal_contract.yaml, data_quality_report.json)
- Deterministic output paths
- Explicit overwrite flag (`--overwrite`)

### Out of Scope (Explicitly Forbidden)

- Backtesting
- Performance metrics (Sharpe, drawdown, CAGR, etc.)
- Portfolio construction
- Strategy search
- AlphaForge runtime import
- Live trading
- Broker execution

## Specs Affected

- signal-export-contract (new: CLI export paths)
- data-registry-mvp (new: CLI config-driven loading)
- signal-contract-yaml (new: CLI-generated contract content)

## New Spec Required

- cli-generate-contract (under openspec/specs/cli-generate-contract/spec.md)

This spec will define the CLI command interface, config schema, overwrite behavior, and success output.

## Next Step

Proceed to design.md once this proposal is approved.