# SignalForge-to-AlphaForge Handoff

## Purpose

This document describes how SignalForge signal artifacts are handed off to AlphaForge for validation, backtesting, and evidence evaluation.

**SignalForge does not run AlphaForge backtests.** SignalForge is a signal generation layer only.

---

## SignalForge Output Artifacts

Every `signalforge generate` run produces exactly three artifacts:

| Artifact | Format | Role |
|----------|--------|------|
| signal.csv | CSV | Primary handoff file for AlphaForge custom_signal workflows |
| signal_contract.yaml | YAML | Metadata for auditability and reproducibility |
| data_quality_report.json | JSON | Source OHLCV data quality report |

---

## signal.csv: Primary Handoff File

`signal.csv` is the canonical input for AlphaForge's `custom_signal` strategy interface.

### Required Schema

```
datetime, available_at, symbol, signal_name, signal_value, signal_binary, source
```

### Compatibility Rules

AlphaForge expects:

1. **Required columns exist** - All 7 columns must be present
2. **Datetime is parseable** - ISO 8601 format recommended
3. **available_at <= datetime** - Signal must be available before or at the signal date at daily-date level
4. **signal_binary in {0, 1}** - Binary signal only
5. **Symbol is present** - Ticker symbol populated
6. **No duplicate rows** - Each (datetime, symbol, signal_name) tuple is unique

---

## Daily datetime policy

SignalForge MVP daily OHLCV signal handoff uses daily trading-date alignment.

For `signal.csv`, `datetime` and `available_at` should be interpreted as declared daily trading-date labels. In the OHLCV-only MVP, `available_at` is the same declared trading date as `datetime`.

AlphaForge should align daily signals by the declared trading date and should not UTC-shift the declared date for daily alignment. For example, `2025-01-02T00:00:00+08:00` should align as trading date `2025-01-02`.

This handoff policy does not support intraday event-time validation. SignalForge does not claim point-in-time correctness for non-OHLCV data in MVP.

---

## signal_contract.yaml: Auditability Support

The contract file provides:

- **Factor identity**: name, version, parameters
- **Decision rule**: how signal_binary is derived from signal_value
- **Timing rule**: when the signal is available
- **Data contract**: required input columns
- **Output schema**: canonical column order

This metadata supports:
- Reproducibility of signal generation
- Audit trails for evidence
- Compliance documentation

---

## data_quality_report.json: Source Data Quality

The quality report describes the **source OHLCV market data** used to generate signals:

- Dataset name and source type
- Symbol count and row count
- Date range
- Duplicate rows
- Missing values per OHLCV column (open, high, low, close, volume)
- Warnings (null values, price integrity violations)
- **point_in_time_correctness_claimed: false** - SignalForge makes no PIT correctness claims in MVP

---

## Manual Handoff Example

```bash
# Step 1: Generate signals with SignalForge
signalforge generate --config examples/twse_2330_moskowitz_signal.yaml --overwrite

# Step 2: Locate the signal.csv
OUTPUT_DIR="artifacts/TWSE_2330/moskowitz_momentum/20210104_20241231"
SIGNAL_FILE="${OUTPUT_DIR}/signal.csv"

# Step 3: Use as AlphaForge custom_signal input
alphaforge research-validate \
    --strategy custom_signal \
    --data <market_data.csv> \
    --signal-file "${SIGNAL_FILE}"

# Step 4: AlphaForge performs validation, backtesting, and evidence evaluation
```

---

## AlphaForge Responsibilities

After handoff, AlphaForge is responsible for:

- **Backtesting** - Walk-forward analysis, out-of-sample testing
- **Performance metrics** - Sharpe, drawdown, CAGR, etc.
- **Evidence diagnostics** - Regime analysis, factor exposure
- **Final holdout evaluation** - Out-of-sample verdict
- **Reports** - Summary generation

SignalForge does **not** compute these. It only generates the signal artifacts.

---

## Key Points

- SignalForge does **not run backtests**
- SignalForge does **not compute performance metrics**
- SignalForge does **not import AlphaForge**
- AlphaForge remains the validation backend
- SignalForge artifacts are **deterministic** - same input produces same output

---

## Integration Command

```bash
alphaforge research-validate --strategy custom_signal --data <market_data.csv> --signal-file <signal.csv>
```

SignalForge exports compatible artifacts. AlphaForge runs the evidence pipeline.
