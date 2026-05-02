# Data Registry MVP

## Purpose

Define the MVP scope for SignalForge data registry: loading, normalizing, and quality-checking OHLCV market data.

## Owner

SignalForge

## Requirements

### Requirement: Data Loading

SignalForge SHALL load OHLCV data from configured data sources and SHALL support CSV file input (MVP).

#### Scenario: CSV Loading
- **WHEN** A CSV file with OHLCV data is provided
- **THEN** SignalForge SHALL load and parse the data

### Requirement: Required OHLCV Columns

The following columns SHALL be required: datetime, open, high, low, close, volume.

#### Scenario: Missing Required Columns
- **WHEN** Required OHLCV columns are absent
- **THEN** SignalForge SHALL raise MissingColumnsError

### Requirement: Data Normalization

SignalForge SHALL convert datetime columns to pandas.Timestamp with UTC timezone and SHALL ensure lowercase column names.

#### Scenario: Datetime Normalization
- **WHEN** OHLCV data is loaded
- **THEN** Datetime columns SHALL be converted to UTC Timestamps

### Requirement: Quality Checks

SignalForge SHALL perform quality checks and SHALL record issues in data_quality_report.json.

#### Scenario: Null Value Detection
- **WHEN** Null values are present in OHLCV columns
- **THEN** They SHALL be recorded in data_quality_report.json

#### Scenario: Price Integrity Check
- **WHEN** Invalid price relationships are detected (high < low)
- **THEN** They SHALL be recorded as warnings

### Requirement: Duplicate Timestamp Handling

SignalForge SHALL deduplicate timestamps, keeping the first occurrence.

#### Scenario: Duplicate Handling
- **WHEN** Duplicate timestamps are found
- **THEN** SignalForge SHALL keep the first and discard subsequent duplicates

### Requirement: Error Handling

SignalForge SHALL raise MissingColumnsError for missing columns and DataQualityError for critical failures.

#### Scenario: Error Reporting
- **WHEN** Errors occur during data loading
- **THEN** They SHALL be logged and do not halt export
