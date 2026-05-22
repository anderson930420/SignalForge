# alphaforge-compatibility-smoke-export Specification

## MODIFIED Requirements

### Requirement: Market Data Contract

`market_data.csv` SHALL contain the following columns in order:

1. `datetime`
2. `open`
3. `high`
4. `low`
5. `close`
6. `volume`

The market data SHALL satisfy:

- The declared daily trading-date set SHALL exactly match the `signal.csv` declared daily trading-date set
- Offset timestamps SHALL preserve their declared calendar date during package normalization and readback validation
- `open`, `high`, `low`, and `close` SHALL be finite and positive
- `high >= low`
- `high >= open`
- `high >= close`
- `low <= open`
- `low <= close`
- `volume` SHALL be present

#### Scenario: Offset timestamp package normalization

- **WHEN** package input contains `datetime` value `2025-01-02T00:00:00+08:00`
- **THEN** the exported package preserves declared trading date `2025-01-02`
- **AND** package readback validation does not UTC-shift it to `2025-01-01`

### Requirement: Signal CSV Contract

`signal.csv` SHALL contain the stable column order:

1. `datetime`
2. `available_at`
3. `symbol`
4. `signal_name`
5. `signal_value`
6. `signal_binary`
7. `source`

The signal rows SHALL satisfy:

- `signal_binary` SHALL contain only `0` or `1`
- `available_at <= datetime` at declared daily trading-date level
- No duplicate `(datetime, symbol, signal_name)` rows SHALL exist after declared daily trading-date normalization
- `row_count` SHALL be greater than 1
- The declared daily trading-date set SHALL exactly match the `market_data.csv` declared daily trading-date set
- `signal_value` SHALL be present for provenance, but AlphaForge SHALL NOT use it for execution

#### Scenario: Signal package daily timing

- **WHEN** `available_at` and `datetime` have the same declared calendar date
- **THEN** the package temporal validation passes
- **WHEN** `available_at` is a later declared calendar date than `datetime`
- **THEN** the package temporal validation fails
