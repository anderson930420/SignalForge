# AlphaForge Compatibility Contract

## MODIFIED Requirements

### Requirement: signal.csv Validation

The validation SHALL verify: 7 columns, correct column order, ISO 8601 datetime format, binary values 0 or 1 only, available_at <= datetime at daily-date level for MVP daily OHLCV signals, and NOT NULL constraints.

For SignalForge MVP daily OHLCV signals, compatibility helpers SHALL normalize `datetime` and `available_at` to naive midnight `pandas.Timestamp` values using the declared calendar date in the input value. Helpers SHALL NOT UTC-shift offset timestamps before extracting the daily trading date.

#### Scenario: Offset timestamp daily validation

- **WHEN** a signal row contains `datetime` value `2025-01-02T00:00:00+08:00`
- **THEN** compatibility validation treats the row as declared trading date `2025-01-02`
- **AND** validation does not normalize it to UTC date `2025-01-01`

#### Scenario: Daily available_at validation

- **WHEN** `available_at` has the same declared daily trading date as `datetime`
- **THEN** temporal validation passes
- **WHEN** `available_at` has a later declared daily trading date than `datetime`
- **THEN** temporal validation fails

### Requirement: Cross-Artifact Validation

The validation SHALL verify declared daily trading-date alignment between signal rows and market data.

#### Scenario: Declared trading-date alignment

- **WHEN** market data has declared date `2025-01-02`
- **AND** signal data has declared datetime `2025-01-02T00:00:00+08:00`
- **THEN** daily alignment validation passes

#### Scenario: Declared trading-date mismatch

- **WHEN** signal declared daily trading dates differ from market declared daily trading dates
- **THEN** daily alignment validation fails

#### Scenario: Invalid datetime reporting

- **WHEN** a daily datetime-like value cannot be parsed
- **THEN** compatibility validation reports the invalid field clearly
