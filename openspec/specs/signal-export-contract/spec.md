# Signal Export Contract

## Purpose

Define the export pipeline that writes signal artifacts to disk with deterministic layout.

## Owner

SignalForge

## Requirements

### Requirement: Export Artifacts

SignalForge SHALL export signal.csv, signal_contract.yaml, and data_quality_report.json for every signal generation run.

#### Scenario: All Artifacts Exported
- **WHEN** Signal generation completes
- **THEN** All three artifacts SHALL be created

### Requirement: Directory Structure

Artifacts SHALL be written to {artifacts_dir}/{symbol}/{datetime_range}/ directory structure.

#### Scenario: Directory Structure Compliance
- **WHEN** Artifacts are written
- **THEN** They SHALL follow the specified directory structure

### Requirement: CSV Export Rules

The signal.csv export SHALL use specified column order, SHALL NOT include an index column, SHALL use UTF-8 encoding, and SHALL use Unix line terminator (LF).

#### Scenario: CSV Format Compliance
- **WHEN** signal.csv is written
- **THEN** It SHALL follow all specified format rules

### Requirement: YAML Export Rules

The signal_contract.yaml export SHALL follow signal-contract-yaml schema and SHALL contain non-empty signals list.

#### Scenario: YAML Schema Compliance
- **WHEN** signal_contract.yaml is written
- **THEN** It SHALL follow the schema specification

### Requirement: JSON Export Rules

The data_quality_report.json export SHALL follow data-quality-report schema and SHALL populate all quality metrics.

#### Scenario: JSON Schema Compliance
- **WHEN** data_quality_report.json is written
- **THEN** It SHALL follow the schema specification

### Requirement: Determinism

Given the same input data and factor configuration, export SHALL produce byte-for-byte identical artifacts.

#### Scenario: Deterministic Output
- **WHEN** Export is run twice with identical inputs
- **THEN** Output SHALL be byte-for-byte identical

### Requirement: Error Handling

Write permission denied, disk full, and invalid data SHALL raise ExportError with details.

#### Scenario: Export Error Handling
- **WHEN** Export fails due to system errors
- **THEN** ExportError SHALL be raised with details
