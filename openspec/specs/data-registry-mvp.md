# Data Registry MVP

## Type

Capability Specification

## Purpose

Define the MVP scope for SignalForge data registry: loading, normalizing, and quality-checking OHLCV market data.

## Owner

SignalForge

## Responsibility

`data_registry.py` owns data loading, normalization, and quality checks for OHLCV input data.

## Core Capabilities

### Data Loading

- Load OHLCV data from configured data sources
- Support CSV file input (MVP)
- Normalize column names to lowercase OHLCV standard

### Required OHLCV Columns

| Column | Type | Description |
|--------|------|-------------|
| datetime | timestamp | Bar timestamp |
| open | float | Opening price |
| high | float | High price |
| low | float | Low price |
| close | float | Closing price |
| volume | float | Trading volume |

### Data Normalization

- Convert datetime columns to pandas.Timestamp with UTC timezone
- Ensure lowercase column names
- Parse symbol from filename or metadata

### Quality Checks

| Check | Behavior on Failure |
|-------|---------------------|
| Missing required columns | Raise DataQualityError with column name |
| Null values in OHLCV | Record in data_quality_report.json |
| Invalid price relationships | Record warning (high >= low, high >= open, etc.) |
| Duplicate timestamps | Deduplicate, keep first |

### MVP Exclusion

Future capabilities (non-MVP):
- Multi-source data contracts
- Database connectors
- Real-time data streams
- Data caching layer

## Output

Returns a normalized pandas.DataFrame with OHLCV data ready for factor calculation.

## Error Handling

- MissingColumnsError: Raised when required OHLCV columns are absent
- DataQualityError: Raised for critical data quality failures
- Errors are logged and do not halt export (quality issues go to report)
