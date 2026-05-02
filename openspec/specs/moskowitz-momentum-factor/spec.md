# Moskowitz Momentum Factor

## Purpose

Define the Moskowitz Momentum Factor implementation for SignalForge MVP.

## Owner

SignalForge

## Requirements

### Requirement: Factor Source

The Moskowitz Momentum Factor SHALL be based on Moskowitz, Ostdie, and Wells (2024): "Into the Darkness: An Empirical Investigation of Dark Matter Returns".

#### Scenario: Source Attribution
- **WHEN** Factor is documented
- **THEN** It SHALL reference the correct source paper

### Requirement: Factor Definition

The factor SHALL measure trailing 12-month risk-adjusted return trend.

#### Scenario: Factor Purpose
- **WHEN** Factor is described
- **THEN** It SHALL reflect its purpose as defined

### Requirement: Calculation Formula

The factor SHALL use the formula: signal_value = (CUMRET_12M - CUMRET_1M) / VOL_1M.

#### Scenario: Formula Application
- **WHEN** Factor is calculated
- **THEN** It SHALL use the specified formula

### Requirement: Implementation Parameters

The factor SHALL use 252 trading days lookback, 21 trading days short-term lag, and 21 trading days volatility window.

#### Scenario: Parameter Usage
- **WHEN** Factor calculation occurs
- **THEN** It SHALL use the specified parameters

### Requirement: Edge Case Handling

Insufficient history, zero volatility, and missing price data SHALL result in signal_value = NaN.

#### Scenario: Zero Volatility Handling
- **WHEN** Volatility is zero
- **THEN** signal_value SHALL be NaN

#### Scenario: Missing Data Handling
- **WHEN** Price data is missing
- **THEN** signal_value SHALL be NaN for affected periods

### Requirement: Output Schema

The returned DataFrame SHALL contain signal_value column.

#### Scenario: Output Column Presence
- **WHEN** Factor calculation completes
- **THEN** Output SHALL contain signal_value column

### Requirement: Required Input

The factor SHALL require datetime and close columns.

#### Scenario: Input Validation
- **WHEN** Factor is called without required columns
- **THEN** It SHALL handle gracefully

### Requirement: Factor Metadata

The factor SHALL have name "moskowitz_momentum" and source "moskowitz_2024".

#### Scenario: Metadata Accuracy
- **WHEN** Factor metadata is accessed
- **THEN** It SHALL have correct name and source
