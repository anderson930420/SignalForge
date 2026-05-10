# Proposal: Align Canonical Signal Artifact Package

## Change Name

align-canonical-signal-artifact-package

## What

Align the normal SignalForge generate pipeline with the canonical daily signal artifact contract.

## Why

SignalForge v0.1 currently generates a single-row signal artifact and omits the canonical signal_name segment in the output path. The canonical boundary requires row-level daily signal output, deterministic packaging, and explicit AlphaForge compatibility metadata.

## User Impact

A user running `signalforge generate` will receive a daily row-level `signal.csv` under:

```text
{artifacts_dir}/{symbol}/{signal_name}/{start_date}_{end_date}/
```

The exported contract will also include the canonical AlphaForge compatibility block.

## Scope

### In Scope

- Row-level daily `signal.csv` generation
- Output path alignment with `signal_name`
- Default validation that signal dates match selected OHLCV dates
- Warmup row support with `signal_value` null and `signal_binary = 0`
- Canonical compatibility metadata in `signal_contract.yaml`
- Test updates for canonical contract behavior

### Out of Scope

- AlphaForge backtesting
- Performance metrics
- Portfolio construction
- Shorting or leverage support
- New factors

