# CI CHANGELOG

### Planned: ps-lint graduation (scripts/**)
We will promote **ps-lint** to required **only for changes under `scripts/**`** after 7 consecutive green days post-flip. Helper: `scripts/pslint-promote.ps1` (print/execute). No action today.

# CI CHANGELOG (Oct 2025)

## What changed
- **Composite guard**: centralized attic/workflow short-circuit logic (uses: ./.github/actions/guard).
- **Only 3 required checks** remain: audit, fast-tests (ubuntu-latest), fast-tests (windows-latest).
- **Lock-first installs** + weekly lock refresh with delta + audit summary.
- **ps-lint** path-filtered to scripts/** (non-blocking burn-in).
- **Guard verifier** (non-blocking) and **required-checks assert** (diagnostic).
- **Dependabot workflow-only**: auto-label & auto-enable squash auto-merge once the 3 required checks are green.

## Why
- Keep CI quiet, fast, and deterministic; reduce reviewer churn; protect branch policy.
