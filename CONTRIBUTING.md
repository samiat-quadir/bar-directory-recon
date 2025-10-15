# Contributing Guide

## Workflow policy (allow-list)
Only these may use `pull_request`/`push`: `fast-parity-ci.yml`, `pip-audit.yml`, `ps-lint.yml` (path-filtered to `scripts/**`), `ci-workflow-guard.yml`, and `codeql*`. Everything else is `workflow_dispatch` or `schedule`.

## Composite guard
Workflow-only/attic changes **short-circuit** fast-tests and audit via a composite guard action; Dependabot workflow-only PRs are auto-labeled and auto-enable **squash auto-merge** once the required checks are green.

## ps-lint (scripts/**) promotion decision
If the next 7 days remain green for `scripts/**`, we will propose adding `ps-lint (ubuntu/windows)` to required checks **only for PRs touching `scripts/**`**. Target decision: **2025-10-15**.

## ps-lint promotion (planned)
- Scope: only for PRs touching `scripts/**`.
- Criteria: 7 consecutive days with ps-lint green.
- Change control: run `scripts/pslint-promote.ps1 -Execute` (maintainers only) to add ps-lint to required checks; rollback by removing those two contexts and re-PUT.
