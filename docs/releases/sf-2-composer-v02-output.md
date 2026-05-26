# SignalForge SF-2 Composer v0.2 Output

## Summary

This phase lets `SignalComposer` explicitly produce v0.2 signal rows while preserving the existing v0.1 default behavior.

## Default Behavior

The default contract remains v0.1:

```text
signal_value
signal_binary
```

Existing CLI and export workflows remain unchanged.

## Opt-in v0.2 Behavior

Callers can request v0.2 output explicitly:

```python
composer.compose(
    factor_output,
    source="SignalForge",
    contract_version="v0.2",
)
```

v0.2 output columns are:

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

This phase does not wire v0.2 into `signalforge generate` YAML config or the export path. That remains a later phase.

SignalForge still emits alpha semantics only. Execution actions such as Buy, Sell, Close Long, Close Short, and Hold remain downstream execution-engine concepts.