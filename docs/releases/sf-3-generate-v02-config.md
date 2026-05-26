# SignalForge SF-3 Generate v0.2 Config

## Summary

This phase wires v0.2 signal output into the `signalforge generate` YAML configuration path while preserving v0.1 as the default.

## Default

If `signal_contract_version` is omitted, `signalforge generate` still emits v0.1:

```text
signal_value
signal_binary
```

## v0.2 Opt-in

A config can request v0.2 output:

```yaml
signal_contract_version: v0.2
target_weight:
  method: signed_unit
  max_abs_weight: 1.0
  neutral_threshold: 0.0
```

The generated `signal.csv` uses:

```text
datetime
available_at
symbol
signal_name
score
direction
target_weight
source
```

## Boundary

This phase does not add AlphaForge execution, optimization, or backtesting inside SignalForge. SignalForge remains the producer of alpha semantics.
