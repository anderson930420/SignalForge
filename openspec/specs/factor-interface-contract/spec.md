# Factor Interface Contract

## Purpose

Define the protocol for factor implementations in SignalForge.

## Owner

SignalForge

## Requirements

### Requirement: Factor Protocol Conformance

All factor implementations SHALL conform to the FactorProtocol defined in factor_base.py.

#### Scenario: Protocol Conformance
- **WHEN** A factor is implemented
- **THEN** It SHALL implement name, source, and calculate()

### Requirement: Required Attributes

Factors SHALL have name (str) and source (str) attributes.

#### Scenario: Attribute Presence
- **WHEN** A factor is inspected
- **THEN** It SHALL have name and source attributes

### Requirement: Calculate Method Signature

The calculate(data: pd.DataFrame) -> pd.DataFrame method SHALL accept OHLCV columns and SHALL return a DataFrame with 'signal_value' column.

#### Scenario: Calculate Method Behavior
- **WHEN** calculate() is called with valid OHLCV data
- **THEN** It SHALL return a DataFrame with signal_value column

### Requirement: Pure Function

The calculate method SHALL be pure and SHALL NOT modify the input DataFrame.

#### Scenario: Input Preservation
- **WHEN** calculate() is executed
- **THEN** The input DataFrame SHALL NOT be modified

### Requirement: Null Handling

Factors SHALL handle null OHLCV values gracefully and SHALL NOT silently drop null signal_values.

#### Scenario: Null Signal Values
- **WHEN** Input data contains null values
- **THEN** signal_value SHALL be explicitly NaN, not silently dropped

### Requirement: Determinism

Factor calculation SHALL be deterministic: same input SHALL produce same output.

#### Scenario: Deterministic Output
- **WHEN** calculate() is called twice with the same data
- **THEN** Output SHALL be identical

### Requirement: Implementation Location

Factor implementations SHALL reside in the factors/ directory.

#### Scenario: Location Verification
- **WHEN** A factor implementation is created
- **THEN** It SHALL be placed in the factors/ directory
