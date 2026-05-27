# SignalForge SF-7 Taiwan Multi-Symbol Pipeline

## Summary

This phase adds script-level support for running a Taiwan multi-symbol OHLCV pipeline.

The pipeline keeps external data-source handling outside the SignalForge core package.

## Flow

```text
symbols
  -> download OHLCV CSVs
  -> write per-symbol v0.2 configs
  -> run signalforge generate
  -> run package-alphaforge-v02
  -> write tw_multi_symbol_summary.json
```

## Example

```bash
python3 scripts/run_tw_multi_symbol_pipeline.py \
  --symbols 2330.TW,0050.TW,2317.TW \
  --start 2020-01-01 \
  --end 2025-01-01 \
  --output-root artifacts/tw_multi_symbol \
  --overwrite
```

## Output Shape

```text
artifacts/tw_multi_symbol/
  data/
  configs/
  artifacts/
  packages/
  tw_multi_symbol_summary.json
```

Each package under `packages/<symbol>/` can be consumed by AlphaForge:

```bash
PYTHONPATH=src python3 -m alphaforge.cli smoke-signalforge-package \
  --package ../SignalForge/artifacts/tw_multi_symbol/packages/2330.TW
```

## Boundary

This phase does not change the signal schema.

SignalForge still produces `score`, `direction`, and `target_weight`.

AlphaForge still consumes `target_weight` through `custom_signal` v0.2.
