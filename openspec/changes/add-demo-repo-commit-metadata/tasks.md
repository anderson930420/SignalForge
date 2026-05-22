# Tasks: Add Demo Repository Commit Metadata

## Task 1: Add demo git metadata capture

Status: Complete

**Files:** `scripts/run_signalforge_alphaforge_demo.py`

**Steps:**
1. Add a helper that reads `git rev-parse HEAD`.
2. Add dirty-worktree detection using `git status --short`.
3. Include top-level summary fields for SignalForge and AlphaForge repository path, HEAD commit, and dirty status.
4. Add `--require-clean-repos` to fail only when explicitly requested and a repo is dirty.

## Task 2: Update documentation

Status: Complete

**Files:**
- `docs/demos/signalforge_to_alphaforge_e2e.md`
- `docs/releases/signalforge-alphaforge-e2e-checkpoint.md`

**Steps:**
1. Document the commit metadata fields in the demo summary.
2. Mention clean-repo enforcement for release/checkpoint runs.

## Task 3: Add focused regression coverage

Status: Complete

**Files:** `tests/test_demo_docs.py`

**Steps:**
1. Verify the git metadata helper returns a HEAD commit and dirty status.
2. Verify `--require-clean-repos` rejects dirty repo metadata.
3. Verify the demo docs mention the repository commit metadata fields.

## Task 4: Validate

Status: Complete

**Commands:**
1. `python3 -m pytest tests/test_demo_docs.py`
2. `ruff check scripts/run_signalforge_alphaforge_demo.py tests/test_demo_docs.py`
3. `openspec validate add-demo-repo-commit-metadata --strict`
4. `python3 scripts/run_signalforge_alphaforge_demo.py`
5. `python3 scripts/run_signalforge_alphaforge_demo.py --require-clean-repos`
6. `python3 -m pytest`
7. `ruff check .`
8. `openspec validate --all --strict`
