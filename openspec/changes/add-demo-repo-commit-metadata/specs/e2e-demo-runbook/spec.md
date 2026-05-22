# e2e-demo-runbook Specification

## ADDED Requirements

### Requirement: Demo summary records repository commit metadata

The SignalForge-to-AlphaForge E2E demo SHALL include repository metadata for both SignalForge and AlphaForge in its printed JSON summary.

#### Scenario: Demo summary includes repository identity and HEAD

- **GIVEN** the SignalForge and AlphaForge repositories are available locally
- **WHEN** the demo flow is run
- **THEN** the printed JSON summary includes `signalforge_repo`
- **AND** it includes `signalforge_head`
- **AND** it includes `signalforge_dirty`
- **AND** it includes `alphaforge_repo`
- **AND** it includes `alphaforge_head`
- **AND** it includes `alphaforge_dirty`

#### Scenario: Dirty repositories do not fail by default

- **GIVEN** either repository has dirty git status
- **WHEN** the demo flow is run without clean-repository enforcement
- **THEN** the demo records the dirty status in the summary
- **AND** the demo does not fail merely because a repository is dirty

#### Scenario: Explicit clean-repository enforcement fails dirty runs

- **GIVEN** either repository has dirty git status
- **WHEN** the demo flow is run with clean-repository enforcement
- **THEN** the demo fails before running the cross-repository workflow
