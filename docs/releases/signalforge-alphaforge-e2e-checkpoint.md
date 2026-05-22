# SignalForge + AlphaForge First E2E Checkpoint

## Verdict

FIRST E2E DEMO PASSED.

## Scope

This checkpoint freezes the first successful real end-to-end demo where SignalForge-generated artifacts were consumed by AlphaForge `custom_signal` and used in the AlphaForge research validation/backtest workflow.

This checkpoint covers:

- SignalForge deterministic OHLCV input generation for the demo.
- SignalForge generation of `signal.csv`, `signal_contract.yaml`, and `data_quality_report.json`.
- AlphaForge consumption of the generated `signal.csv` through `custom_signal`.
- AlphaForge research validation/backtest artifact generation.
- Cross-repository validation results for SignalForge and AlphaForge.

This checkpoint does not expand runtime scope, artifact schemas, factor coverage, or execution semantics.

The demo summary now records commit metadata for both repositories: resolved repository paths, `git rev-parse HEAD` commits, and dirty-worktree booleans. Release checkpoint runs should use `--require-clean-repos` when clean pinned SignalForge and AlphaForge commits are required.

## SignalForge Command Used

The demo was run from the SignalForge repository with:

```bash
python3 scripts/run_signalforge_alphaforge_demo.py
```

The script invoked SignalForge with:

```bash
python3 -m signalforge.cli \
  --config artifacts/signalforge_to_alphaforge_e2e/input/signalforge_config.yaml \
  --overwrite
```

## AlphaForge Command Used

The script invoked AlphaForge with the SignalForge-generated `signal.csv`:

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
  --initial-capital 1000 \
  --fee-rate 0 \
  --slippage-rate 0 \
  --annualization-factor 252 \
  --output-dir artifacts/signalforge_to_alphaforge_e2e/alphaforge \
  --experiment-name signalforge_to_alphaforge_e2e
```

## Generated SignalForge Artifacts

SignalForge generated:

```text
artifacts/signalforge_to_alphaforge_e2e/signalforge/SFDEMO/moskowitz_momentum/20240102_20250331/signal.csv
artifacts/signalforge_to_alphaforge_e2e/signalforge/SFDEMO/moskowitz_momentum/20240102_20250331/signal_contract.yaml
artifacts/signalforge_to_alphaforge_e2e/signalforge/SFDEMO/moskowitz_momentum/20240102_20250331/data_quality_report.json
```

## Generated AlphaForge Artifacts

AlphaForge generated:

```text
artifacts/signalforge_to_alphaforge_e2e/alphaforge/signalforge_to_alphaforge_e2e/development_signal/equity_curve.csv
artifacts/signalforge_to_alphaforge_e2e/alphaforge/signalforge_to_alphaforge_e2e/development_signal/experiment_config.json
artifacts/signalforge_to_alphaforge_e2e/alphaforge/signalforge_to_alphaforge_e2e/development_signal/metrics_summary.json
artifacts/signalforge_to_alphaforge_e2e/alphaforge/signalforge_to_alphaforge_e2e/development_signal/trade_log.csv
artifacts/signalforge_to_alphaforge_e2e/alphaforge/signalforge_to_alphaforge_e2e/final_holdout/equity_curve.csv
artifacts/signalforge_to_alphaforge_e2e/alphaforge/signalforge_to_alphaforge_e2e/final_holdout/experiment_config.json
artifacts/signalforge_to_alphaforge_e2e/alphaforge/signalforge_to_alphaforge_e2e/final_holdout/metrics_summary.json
artifacts/signalforge_to_alphaforge_e2e/alphaforge/signalforge_to_alphaforge_e2e/final_holdout/trade_log.csv
artifacts/signalforge_to_alphaforge_e2e/alphaforge/signalforge_to_alphaforge_e2e/research_protocol_summary.json
```

## Validation Results

SignalForge validation:

- `python3 scripts/run_signalforge_alphaforge_demo.py`: passed.
- `python3 -m pytest`: 111 passed.
- `ruff check .`: passed.
- `openspec validate --all --strict`: 16 passed.

AlphaForge validation:

- `python3 -m pytest`: 263 passed.
- `ruff check .`: passed.
- `openspec validate --all --strict`: 27 passed.

## Boundary Confirmations

- SignalForge does not run backtests.
- AlphaForge does not compute SignalForge factors.
- AlphaForge does not import SignalForge runtime; the demo confirmed no SignalForge runtime import during AlphaForge `custom_signal` checks.
- signal_value is ignored for execution; AlphaForge uses `signal_binary` to derive long/flat target positions.

## Known Limitations

- Single-symbol long/flat demo only.
- File-based handoff only.
- No portfolio construction.
- No live trading or broker execution.
- No AlphaForge-side SignalForge factor calculation.
- No SignalForge-side research validation, backtesting, performance search, or final holdout evaluation.
- Demo data is deterministic and local; it is not a production data-source certification.

## Suggested Next Milestones

1. Archive the completed SignalForge OpenSpec changes once the checkpoint is accepted.
2. Commit and tag the SignalForge checkpoint state.
3. Commit and tag the AlphaForge custom-signal readiness state.
4. Add a versioned compatibility matrix for future SignalForge artifact versions and AlphaForge consumers.
5. Add multi-symbol and multi-signal design notes after the single-symbol file handoff remains stable.
6. Keep portfolio construction, live trading, and broker execution out of SignalForge.
