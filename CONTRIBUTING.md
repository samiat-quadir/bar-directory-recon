# Contributing Guide

## ps-lint promotion (planned)
- Scope: only for PRs touching `scripts/**`.
- Criteria: 7 consecutive days with ps-lint green.
- Change control: run `scripts/pslint-promote.ps1 -Execute` (maintainers only) to add ps-lint to required checks; rollback by removing those two contexts and re-PUT.