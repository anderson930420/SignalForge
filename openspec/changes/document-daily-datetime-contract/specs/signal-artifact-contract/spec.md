# Signal Artifact Contract

## MODIFIED Requirements

### Requirement: Column Constraints

The signal artifact columns SHALL have the following constraints:

| Column | Constraint |
|--------|-------------|
| datetime | NOT NULL, ISO 8601 parseable daily trading-date label for MVP daily OHLCV signals |
| available_at | NOT NULL, MUST be <= datetime at daily-date level for MVP daily OHLCV signals |
| symbol | NOT NULL, string |
| signal_name | NOT NULL, string |
| signal_value | MAY BE NULL, float |
| signal_binary | NOT NULL, only 0 or 1 |
| source | NOT NULL, string |

For SignalForge MVP daily OHLCV signals, `datetime` and `available_at` SHALL be interpreted as declared daily trading-date labels. `available_at` SHALL be the same declared trading date as `datetime` for OHLCV-only daily signals. SignalForge SHALL NOT claim intraday event-time availability validation for these fields.

#### Scenario: Daily trading-date labels

- **WHEN** SignalForge emits an MVP daily OHLCV signal row
- **THEN** `datetime` represents the declared daily trading date
- **AND** `available_at` represents the declared daily trading date
- **AND** `available_at` is the same declared trading date as `datetime`

#### Scenario: Offset timestamp daily alignment

- **WHEN** a daily signal timestamp includes an offset such as `2025-01-02T00:00:00+08:00`
- **THEN** downstream daily signal alignment treats it as declared trading date `2025-01-02`
- **AND** alignment does not UTC-shift the declared date to another calendar date

#### Scenario: No intraday timing claim

- **WHEN** SignalForge emits MVP daily OHLCV signals
- **THEN** the signal artifact does not claim intraday event-time availability validation
- **AND** the artifact does not claim point-in-time correctness for non-OHLCV data
