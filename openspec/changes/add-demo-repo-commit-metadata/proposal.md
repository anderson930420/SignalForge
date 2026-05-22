# Proposal: Add Demo Repository Commit Metadata

## Change Name

add-demo-repo-commit-metadata

## What

Add SignalForge and AlphaForge repository commit metadata to the SignalForge-to-AlphaForge E2E demo summary.

## Why

The E2E demo proves a real cross-repository path, but the printed summary does not identify the exact repository revisions used. That makes later audit, reproduction, and release checkpoint review weaker than necessary.

## User Impact

Users and future agents can inspect the demo summary and see the SignalForge and AlphaForge repository paths, HEAD commits, and dirty-worktree status used for the run. A new explicit clean-repo flag can make dirty worktrees fail when a release or checkpoint requires pinned clean state.

## Scope

### In Scope

- Demo script git metadata helper.
- Top-level JSON summary fields for both repositories.
- Optional `--require-clean-repos` failure behavior.
- Documentation and focused regression coverage.

### Out of Scope

- Signal artifact schema changes.
- AlphaForge behavior changes.
- SignalForge runtime imports from AlphaForge.
- Backtesting, portfolio construction, or validation logic inside SignalForge.
