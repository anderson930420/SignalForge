# SignalForge

**Purpose:** SignalForge is a paper-derived factor and standardized signal generation layer. It transforms OHLCV market data and factor definitions into deterministic, AlphaForge-compatible signal artifacts.

**SignalForge is not a backtester.**

---

## Project Boundary

### What SignalForge Owns

- OHLCV data input for signal generation
- Future multi-source data contract boundaries
- Factor calculation
- Signal composition
- signal.csv export
- signal_contract.yaml export
- data_quality_report.json export
- AlphaForge-compatible signal schema validation

### What SignalForge Does Not Own

- Backtesting
- Performance metric ranking (Sharpe, drawdown, CAGR, etc.)
- Final holdout evaluation
- Portfolio construction
- Live trading
- Broker execution
- AlphaForge report generation

**Note:** AlphaForge remains the validation backend for backtesting, evidence evaluation, walk-forward analysis, and final holdout evaluation.

---

## Installation / Development Setup

```bash
git clone https://github.com/anderson930420/SignalForge.git
cd SignalForge
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

---

## Testing and Validation

```bash
python -m pytest
ruff check .
openspec validate --all --strict
```

---

## Quickstart: Generate a Moskowitz Momentum Signal

1. **Prepare your OHLCV data:**
   Place a CSV file with columns: `datetime`, `open`, `high`, `low`, `close`, `volume`

2. **Configure the signal:**
   Edit `examples/twse_2330_moskowitz_signal.yaml` and update `data_source.path` to point to your OHLCV CSV file.

3. **Run the generator:**
   ```bash
   signalforge generate --config examples/twse_2330_moskowitz_signal.yaml --overwrite
   ```

   Or via Python module:
   ```bash
   python -m signalforge.cli generate --config examples/twse_2330_moskowitz_signal.yaml --overwrite
   ```

---

## Input Data Format

SignalForge accepts local OHLCV CSV files with the following required columns:

| Column   | Description |
|----------|-------------|
| datetime | Timestamp (ISO 8601 recommended) |
| open     | Opening price |
| high     | Highest price |
| low      | Lowest price |
| close    | Closing price |
| volume   | Trading volume |
| symbol   | Optional if injected via config |

---

## Output Artifacts

Every signal export produces exactly three artifacts in `{artifacts_dir}/{symbol}/{signal_name}/{start_date}_{end_date}/`:

| Artifact | Format | Description |
|----------|--------|-------------|
| signal.csv | CSV | Row-level signal data |
| signal_contract.yaml | YAML | Signal generation metadata |
| data_quality_report.json | JSON | Source OHLCV data quality report |

---

## signal.csv Contract

**Exact column order:**
```
datetime, available_at, symbol, signal_name, signal_value, signal_binary, source
```

**Rules:**
- `available_at <= datetime` always
- `signal_binary` contains only 0 or 1
- `signal_binary = 1 if signal_value > 0 else 0`
- Rows sorted deterministically by `datetime, symbol, signal_name`
- No duplicate `(datetime, symbol, signal_name)` rows

**Insufficient-history rows:**
Rows where the factor cannot compute a valid value (e.g., warmup period) are dropped before export.

---

## signal_contract.yaml Example

```yaml
signal_name: moskowitz_momentum
version: 0.1.0
source: moskowitz_2024
factor:
  name: moskowitz_momentum
  version: 0.1.0
  parameters:
    lookback_days: 252
decision_rule:
  signal_binary: "1 if signal_value > 0 else 0"
data:
  required_columns:
    - datetime
    - open
    - high
    - low
    - close
    - volume
    - symbol
timing:
  available_at_rule: "same as datetime for OHLCV-only daily signal"
output:
  file: signal.csv
  schema_version: 0.1.0
  columns:
    - datetime
    - available_at
    - symbol
    - signal_name
    - signal_value
    - signal_binary
    - source
```

---

## data_quality_report.json Example

```json
{
  "version": "1.0",
  "generator": "SignalForge",
  "dataset_name": "path/to/ohlcv.csv",
  "source_type": "local_ohlcv_csv",
  "symbol_count": 1,
  "row_count": 1948,
  "start_date": "2018-01-02T00:00:00+00:00",
  "end_date": "2025-12-31T00:00:00+00:00",
  "duplicate_rows": 0,
  "missing_values": {
    "open": 0,
    "high": 0,
    "low": 0,
    "close": 0,
    "volume": 0
  },
  "warnings": [],
  "point_in_time_correctness_claimed": false
}
```

**Note:** This report describes the source OHLCV market data, not the composed signal dataframe.

---

## Current MVP Factor: Moskowitz Time-Series Momentum

**Formula:**
```
signal_value[t] = close[t - skip_days] / close[t - lookback_days] - 1
```

**Parameters:**
| Parameter | Default | Description |
|-----------|---------|-------------|
| lookback_days | 252 | 12 months of trading days |
| skip_days | 21 | 1 month of trading days |

**Insufficient-history policy:**
Rows where `factor_value` is NaN (due to insufficient lookback data) are dropped before signal composition.

---

## Non-Goals

SignalForge does **not** provide:
- Backtesting
- Performance metric ranking (Sharpe, drawdown, CAGR, etc.)
- Live trading
- Broker execution
- Portfolio construction
- Multi-factor portfolio optimization

For these capabilities, use AlphaForge after generating signal artifacts with SignalForge.

---

## AlphaForge Integration

SignalForge exports signal artifacts that AlphaForge can consume through its `custom_signal` strategy interface:

```bash
alphaforge research-validate --strategy custom_signal --data <market_data.csv> --signal-file <signal.csv>
```

SignalForge does not import AlphaForge at runtime.

For detailed handoff documentation, see [docs/alphaforge_handoff.md](docs/alphaforge_handoff.md).