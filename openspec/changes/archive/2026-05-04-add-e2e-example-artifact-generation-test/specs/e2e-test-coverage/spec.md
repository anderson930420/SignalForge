# End-to-End Test Coverage

## Purpose

This change adds end-to-end test coverage for existing CLI and export contracts.

## Owner

SignalForge

## ADDED Requirements

### Requirement: Test Coverage Scope

This change SHALL add test coverage and SHALL NOT modify any public contracts.

#### Scenario: No Contract Changes
- **WHEN** This change is reviewed
- **THEN** No public contracts SHALL be modified

### Requirement: Test File Location

The end-to-end test SHALL be placed in `tests/test_e2e_generate_artifacts.py`.

#### Scenario: Test Location
- **WHEN** E2E test is implemented
- **THEN** It SHALL be in `tests/test_e2e_generate_artifacts.py`

### Requirement: Test Data Constraints

The test SHALL use mock OHLCV data with at least 300 business day rows to support Moskowitz momentum calculation (lookback=252, skip=21).

#### Scenario: Mock Data Sufficiency
- **WHEN** Mock data is generated
- **THEN** It SHALL have at least 300 rows

### Requirement: Artifact Assertions

The test SHALL assert all three artifact files are generated: signal.csv, signal_contract.yaml, data_quality_report.json.

#### Scenario: All Artifacts Generated
- **WHEN** CLI pipeline completes
- **THEN** All three artifacts SHALL exist

### Requirement: Forbidden Test Behavior

The test SHALL NOT compute performance metrics, import AlphaForge runtime, or add backtest logic.

#### Scenario: No Performance Metrics
- **WHEN** Test executes
- **THEN** No performance metrics SHALL be computed

#### Scenario: No AlphaForge Import
- **WHEN** Test executes
- **THEN** AlphaForge runtime SHALL NOT be imported