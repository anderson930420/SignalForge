# SignalForge SF-6 Package Real v0.2 Artifacts for AlphaForge

## Summary

This phase adds a CLI command that packages real `signalforge generate --config` v0.2 artifacts into an AlphaForge-compatible package.

## Workflow

Generate real v0.2 artifacts:

```bash
python3 -m signalforge.cli generate \
  --config configs/2330_moskowitz_v02.yaml \
  --overwrite
```

Package them for AlphaForge:

```bash
python3 -m signalforge.cli package-alphaforge-v02 \
  --artifact-dir artifacts/2330.TW/tw_2330_moskowitz_v02/20200101_20250101 \
  --market-data data/2330_ohlcv.csv \
  --output-dir artifacts/2330.TW/tw_2330_moskowitz_v02/alphaforge_package \
  --overwrite
```

Then consume with AlphaForge:

```bash
python3 -m alphaforge.cli smoke-signalforge-package \
  --package ../SignalForge/artifacts/2330.TW/tw_2330_moskowitz_v02/alphaforge_package
```

## Boundary

SignalForge only packages file artifacts. It does not import AlphaForge, run AlphaForge, or claim backtest/performance metrics.
