# SignalForge to AlphaForge E2E Demo

## Purpose

This demo proves the file-based handoff from SignalForge to AlphaForge using real SignalForge-generated artifacts. SignalForge generates a canonical `signal.csv` package from deterministic OHLCV data; AlphaForge consumes that generated `signal.csv` through `custom_signal` and runs the research-validation/backtest workflow.

## Prerequisites

- SignalForge dependencies installed from this repository.
- AlphaForge available as a sibling repository at `../AlphaForge`, or pass `--alphaforge-repo`.
- AlphaForge dependencies installed in the same Python environment or otherwise importable by the Python launcher used for the demo.

## SignalForge Command

Run the automated demo from the SignalForge repository:

```bash
python3 scripts/run_signalforge_alphaforge_demo.py
```

The script creates a deterministic OHLCV CSV at:

```text
artifacts/signalforge_to_alphaforge_e2e/input/market_data.csv
```

Then it invokes SignalForge with:

```bash
python3 -m signalforge.cli \
  --config artifacts/signalforge_to_alphaforge_e2e/input/signalforge_config.yaml \
  --overwrite
```

## AlphaForge Command

The same script invokes AlphaForge with the generated SignalForge `signal.csv`:

```bash
python3 -m alphaforge.cli research-validate \
  --strategy custom_signal \
  --data artifacts/signalforge_to_alphaforge_e2e/input/market_data.csv \
  --symbol SFDEMO \
  --signal-file artifacts/signalforge_to_alphaforge_e2e/signalforge/SFDEMO/moskowitz_momentum/20240102_20250331/signal.csv \
  --signal-name moskowitz_momentum \
  --development-start 2024-01-02 \
  --development-end 2025-01-31 \
  --holdout-start 2025-02-03 \
  --holdout-end 2025-03-31 \
  --train-size 80 \
  --test-size 20 \
  --step-size 20 \
  --output-dir artifacts/signalforge_to_alphaforge_e2e/alphaforge \
  --experiment-name signalforge_to_alphaforge_e2e
```

## Generated SignalForge Artifacts

SignalForge writes:

```text
artifacts/signalforge_to_alphaforge_e2e/signalforge/SFDEMO/moskowitz_momentum/20240102_20250331/signal.csv
artifacts/signalforge_to_alphaforge_e2e/signalforge/SFDEMO/moskowitz_momentum/20240102_20250331/signal_contract.yaml
artifacts/signalforge_to_alphaforge_e2e/signalforge/SFDEMO/moskowitz_momentum/20240102_20250331/data_quality_report.json
```

## Generated AlphaForge Artifacts

AlphaForge writes research-validation outputs under:

```text
artifacts/signalforge_to_alphaforge_e2e/alphaforge/signalforge_to_alphaforge_e2e/
```

Expected files include development signal outputs, walk-forward outputs, final-holdout outputs, and the persisted research protocol summary.

## Validation Results

The demo script checks:

- `signal.csv` schema validation passes through AlphaForge `custom_signal`.
- `signal_binary` maps to AlphaForge `target_position`.
- Missing signal dates default to flat positions.
- Extra signal dates fail validation.
- AlphaForge does not import the SignalForge runtime during custom-signal checks.
- AlphaForge output artifacts are generated.

Repository gates for this change:

```bash
python3 -m pytest
ruff check .
openspec validate --all --strict
```

Last verified for this demo on 2026-05-22:

- `python3 scripts/run_signalforge_alphaforge_demo.py`: passed.
- SignalForge `python3 -m pytest`: 111 passed.
- SignalForge `ruff check .`: passed.
- SignalForge `openspec validate --all --strict`: 16 passed.

AlphaForge gates for the paired readiness state:

```bash
python3 -m pytest
ruff check .
openspec validate --all --strict
```

Last verified for the sibling AlphaForge repository on 2026-05-22:

- AlphaForge `python3 -m pytest`: 263 passed.
- AlphaForge `ruff check .`: passed.
- AlphaForge `openspec validate --all --strict`: 27 passed.

## Boundary Notes

- SignalForge does not run backtests.
- AlphaForge does not compute SignalForge factors.
- AlphaForge does not import SignalForge runtime.
- signal_value is ignored for execution; AlphaForge uses `signal_binary` for long/flat target positions.

## Known Limitations

- Single-symbol long/flat demo only.
- File-based handoff only.
- No portfolio construction.
- No live trading or broker execution.
- No AlphaForge-side factor calculation.
- No SignalForge-side performance search or holdout evaluation.
