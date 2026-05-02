# Data Quality Report

## Purpose

Define the schema and generation rules for data_quality_report.json artifacts.

## Owner

SignalForge

## Requirements

### Requirement: Report Schema

The data_quality_report.json SHALL contain version, exported_at, generator, data_source, quality_metrics, and issues.

#### Scenario: Required Top-Level Keys
- **WHEN** data_quality_report.json is created
- **THEN** It SHALL include all required keys

### Requirement: Quality Metrics Structure

The quality_metrics SHALL include ohlcv_completeness, price_integrity, and temporal_integrity.

#### Scenario: Metric Completeness
- **WHEN** quality_metrics is populated
- **THEN** It SHALL include all three metric categories

### Requirement: Issue Codes

SignalForge SHALL use standardized issue codes: NULL_OHLCV, PRICE_INTEGRITY_VIOLATION, DUPLICATE_TIMESTAMP, MISSING_BARS.

#### Scenario: Issue Code Usage
- **WHEN** Issues are recorded
- **THEN** They SHALL use standardized issue codes

### Requirement: Severity Levels

Issues SHALL have severity of either warning or error.

#### Scenario: Severity Assignment
- **WHEN** An issue is identified
- **THEN** It SHALL be classified as warning or error

### Requirement: Constraint Validation

total_rows SHALL equal row_count from data_source and violation counts SHALL be >= 0.

#### Scenario: Constraint Checking
- **WHEN** Quality metrics are validated
- **THEN** Constraints SHALL be verified

### Requirement: Co-location

The data_quality_report.json SHALL be co-located with signal.csv and signal_contract.yaml.

#### Scenario: Artifact Location
- **WHEN** Artifacts are exported
- **THEN** data_quality_report.json SHALL be in the same directory
