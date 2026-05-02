# SignalForge Agent Instructions

## Project Identity

SignalForge is a paper-derived factor and standardized signal generation layer.

SignalForge is not a backtester.

SignalForge exists to transform input market data and factor definitions into standardized signal artifacts that can later be validated by AlphaForge.

## SignalForge Owns

- OHLCV data input for signal generation
- future multi-source data contract boundaries
- factor calculation
- signal composition
- signal.csv export
- signal_contract.yaml export
- data_quality_report.json export
- AlphaForge-compatible signal schema validation

## SignalForge Does Not Own

- backtesting
- strategy search over performance metrics
- final holdout evaluation
- portfolio construction
- live trading
- broker execution
- AlphaForge report generation

## Boundary With AlphaForge

AlphaForge remains the validation backend.

SignalForge may export signal.csv artifacts that AlphaForge can consume through a custom_signal interface.

SignalForge must not import AlphaForge in MVP unit tests.

SignalForge compatibility checks should be pure schema validation.

## Development Method

Use OpenSpec before non-trivial changes.

For each meaningful change:

1. Create or update an OpenSpec change.
2. Keep the change scope narrow.
3. Implement only behavior covered by the spec.
4. Add tests for public contracts.
5. Run pytest, ruff, and OpenSpec validation.
6. Do not archive until tests and specs pass.

## Universal Workflow

These instructions apply to Codex, opencode, and any other coding agent working in this repository.

Before making changes:

1. Read this file.
2. Inspect the current workspace state.
3. Find the smallest relevant files and constraints before editing.

For task execution:

1. Keep the change scope narrow.
2. Stay inside the SignalForge boundaries defined above.
3. Prefer repo-native scripts and tests over ad hoc workarounds.
4. Before each meaningful action, run `python3 scripts/read_memory.py` and review `01 Projects/SignalForge/worklog.md`.
5. After each meaningful action, append one step log with `python3 src/obsidian_logger.py <log-file-or-string>`.
6. Every step log must use the required `### [YYYY-MM-DD HH:MM] Step: ...` header format.
7. If the task is an Obsidian memory task, use `scripts/read_memory.py` and `src/obsidian_logger.py` only, and write only to `01 Projects/SignalForge/worklog.md`.
8. Do not modify Daily notes or AlphaForge-related Obsidian content.
9. Deduplicate log entries before appending.

## Architecture Rules

- schemas.py contains passive data models and schema constants only.
- data_registry.py owns data loading, normalization, and quality checks.
- factor_base.py owns the factor protocol.
- factor_registry.py owns factor registration and factor config validation.
- signal_composer.py owns conversion from factor output to signal artifact rows.
- export.py owns artifact writing and deterministic file layout.
- compatibility.py owns pure AlphaForge-compatible schema checks.
- factors/ contains factor implementations.
- No backtest.py in MVP.
- No performance metric ranking.
- No portfolio logic.

## Required Signal Artifact

signal.csv must use this stable column order:

```text
datetime
available_at
symbol
signal_name
signal_value
signal_binary
source
```

Required artifacts for every export:

signal.csv
signal_contract.yaml
data_quality_report.json

Testing Rules

Tests should verify:

required signal columns
deterministic signal export
signal_binary only contains 0 or 1
available_at <= datetime
no duplicate datetime-symbol-signal_name rows
missing OHLCV columns fail clearly
FactorRegistry rejects unknown and duplicate factors
SignalForge does not import AlphaForge
SignalForge does not run backtests

```
