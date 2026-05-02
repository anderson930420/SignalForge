# Factor Registry Contract

## Purpose

Define the factor registry that manages factor registration, configuration validation, and lookup.

## Owner

SignalForge

## Requirements

### Requirement: Registry Interface

The FactorRegistry SHALL provide register(), get(), list_factors(), and validate_config() methods.

#### Scenario: Registry Methods
- **WHEN** FactorRegistry is used
- **THEN** It SHALL provide all specified methods

### Requirement: Registration Rules

Unknown factor requests SHALL raise UnknownFactorError and duplicate registrations SHALL raise DuplicateFactorError.

#### Scenario: Reject Unknown Factor
- **WHEN** FactorRegistry.get() is called with unknown name
- **THEN** It SHALL raise UnknownFactorError

#### Scenario: Reject Duplicate Registration
- **WHEN** A factor with existing name is registered
- **THEN** It SHALL raise DuplicateFactorError

### Requirement: Config Validation

Invalid factor config SHALL raise InvalidFactorConfigError.

#### Scenario: Config Validation Failure
- **WHEN** validate_config() receives invalid config
- **THEN** It SHALL raise InvalidFactorConfigError

### Requirement: MVP Scope

SignalForge MVP registry SHALL support in-memory storage, synchronous lookup, and basic config validation.

#### Scenario: MVP Feature Set
- **WHEN** MVP registry is implemented
- **THEN** It SHALL include only MVP features

### Requirement: Future Capability Exclusion

The MVP registry SHALL NOT include persistent registry, factor versioning, or plugin discovery.

#### Scenario: Feature Scope Enforcement
- **WHEN** Feature decisions are made
- **THEN** The implementation SHALL exclude non-MVP features
