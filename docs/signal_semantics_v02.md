# SignalForge Signal Semantics v0.2

## Purpose

SignalForge is the signal producer. It should emit alpha semantics, not execution actions.

The v0.2 producer-side signal vocabulary is:

```text
score
direction
target_weight
```

The canonical v0.2 signal.csv columns are:

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

## Core Rules

`score` is the continuous signed alpha value.

`direction` is ternary:

```text
score > 0  -> +1
score = 0  -> 0
score < 0  -> -1
```

`target_weight` is signed desired exposure:

```text
direction +1 -> positive target_weight
direction  0 -> 0.0
direction -1 -> negative target_weight
```

For SF-1, the default signed unit policy is:

```text
target_weight = direction * max_abs_weight
```

where `0 < max_abs_weight <= 1.0`.

## Boundary

SignalForge must not encode execution actions such as:

- Buy
- Sell
- Close Long
- Close Short
- Hold

Those actions belong to AlphaForge or another execution engine and are derived from:

```text
current_weight -> target_weight
```

## Compatibility

The v0.2 output is designed to match AlphaForge's `custom_signal` v0.2 consumer contract.
