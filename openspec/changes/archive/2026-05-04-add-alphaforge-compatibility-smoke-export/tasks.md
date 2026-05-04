# Tasks: AlphaForge Compatibility Smoke Export Package

## Task 1: Define Package Contract

**Files:** `openspec/changes/add-alphaforge-compatibility-smoke-export/specs/alphaforge-compatibility-smoke-export/spec.md`

**Steps:**
1. Define the package directory and required file set.
2. Specify the required schema and cross-file consistency rules.
3. Capture the AlphaForge consumption boundary for the smoke package.

**Verification:**
- Package contract covers every required artifact in the target directory.

## Task 2: Add Boundary Delta

**Files:** `openspec/changes/add-alphaforge-compatibility-smoke-export/specs/project-boundary/spec.md`

**Steps:**
1. Add an explicit no-AlphaForge-import/no-AlphaForge-dependency requirement for the smoke package.
2. Keep the scope limited to the compatibility boundary.

**Verification:**
- Boundary language remains consistent with SignalForge ownership rules.

## Task 3: Validate Change

**Files:** `openspec/changes/add-alphaforge-compatibility-smoke-export/*`

**Steps:**
1. Run strict OpenSpec validation for the change.
2. Confirm no runtime code or tests were modified.

**Verification:**
- `openspec validate add-alphaforge-compatibility-smoke-export --strict` passes
- `openspec validate --all --strict` passes
