# Workflow Guard Implementation

This document describes the workflow guard system implemented in PR-B to keep CI quiet by restricting automatic triggers to only essential workflows.

## Overview

The workflow guard ensures that only critical workflows run automatically on pull requests and pushes, while all other workflows are converted to manual-only execution. This reduces CI noise and resource consumption while maintaining essential quality gates.

## Active Workflows (Automatic Triggers)

These workflows run automatically on `pull_request` and `push` to `main`:

1. **fast-parity-ci.yml** - Essential cross-platform testing
   - Runs fast tests on Ubuntu and Windows
   - Uses lockfile-aware installation logic
   - Critical for code quality assurance

2. **pip-audit.yml** - Security vulnerability scanning
   - Scans for known vulnerabilities in dependencies
   - Uses lockfile when available for consistent scanning
   - Critical for security compliance

## Manual-Only Workflows

All other workflows have been converted to `workflow_dispatch` (manual-only) triggers:

- `auto-merge.yml` - Manual merge automation
- `ci-fast-parity.yml` - Alternative CI configuration
- `ci-test.yml` - Alternative test configuration
- `ci.yml` - Legacy CI configuration
- `codeql.yml` - Code quality scanning
- `devcontainer-validate.yml` - Container validation
- `filename-guard.yml` - File naming enforcement
- `lock-drift-check.yml` - Dependency drift monitoring
- `pre-commit.yml` - Pre-commit hook validation
- `ps-lint.yml` - PowerShell script linting
- `ruff-strict.yml` - Strict Python linting
- `stale.yml` - Stale issue management
- `verify-scripts.yml` - Script validation

## Benefits

1. **Reduced CI Noise**: Only essential workflows run automatically
2. **Resource Efficiency**: Lower compute usage and faster feedback
3. **Focused Quality Gates**: Clear distinction between critical and optional checks
4. **Flexible Testing**: Manual workflows can be triggered when needed
5. **Supply Chain Security**: Maintains security scanning while reducing overhead

## Usage

### Running Manual Workflows

To run any manual-only workflow:

```bash
# Via GitHub UI: Actions tab -> Select workflow -> Run workflow button
# Via GitHub CLI:
gh workflow run "workflow-name.yml"
```

### Adding New Workflows

When adding new workflows:

- **Critical workflows** (testing, security): Use `pull_request` + `push` triggers
- **Optional workflows** (documentation, cleanup): Use `workflow_dispatch` only

## Implementation Details

The workflow guard was implemented in PR-B as part of the supply-chain stability initiative. It works in conjunction with:

- Lockfile-based dependency management (from PR-A)
- Constraint-based security updates
- Automated dependency auditing

This creates a robust, quiet CI system that maintains quality while reducing noise.
