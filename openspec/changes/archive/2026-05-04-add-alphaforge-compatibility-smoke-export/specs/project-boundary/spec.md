# Project Boundary

## ADDED Requirements

### Requirement: Smoke Export Boundary

The AlphaForge compatibility smoke export package SHALL be produced without importing AlphaForge and SHALL NOT add AlphaForge as a SignalForge dependency.

#### Scenario: No AlphaForge Runtime Coupling
- **WHEN** the smoke export package is defined or later implemented
- **THEN** SignalForge SHALL remain isolated from AlphaForge internals and dependencies
