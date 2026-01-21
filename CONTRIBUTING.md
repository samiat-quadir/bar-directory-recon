# Contributing to bar-directory-recon

Thank you for your interest in contributing! This document outlines the workflow and guidelines for contributing to this project.

## 🚫 Direct Commits to Main Are Disabled

This repository enforces a **branch → PR → merge** workflow. Direct commits to `main` are blocked by:

1. **Local pre-commit hook** - Prevents commits on `main` before they happen
2. **GitHub branch protection** - Rejects pushes to `main` without a PR

## Development Workflow

### 1. Create a Feature Branch

Always start by creating a branch from `main`:

```bash
git checkout main
git pull origin main
git checkout -b feature/your-feature-name
```

Branch naming conventions:
- `feature/` - New features or enhancements
- `fix/` - Bug fixes
- `chore/` - Maintenance tasks, dependency updates
- `docs/` - Documentation changes
- `refactor/` - Code refactoring without behavior changes

### 2. Make Your Changes

- Write clear, focused commits
- Follow the existing code style
- Add tests for new functionality
- Update documentation as needed

### 3. Run Local Checks

Before pushing, ensure your code passes all checks:

```bash
# Run pre-commit hooks
pre-commit run --all-files

# Run tests
pytest -v

# Check coverage
pytest --cov=src --cov=universal_recon --cov-report=term-missing
```

### 4. Push and Create a Pull Request

```bash
git push -u origin feature/your-feature-name
```

Then open a Pull Request on GitHub:
- Use a clear, descriptive title
- Reference any related issues
- Fill out the PR template

### 5. Address Review Feedback

- Respond to review comments
- Push additional commits to address feedback
- Request re-review when ready

### 6. Merge

Once approved and all CI checks pass:
- The PR will be merged via GitHub
- Delete your feature branch after merge

## Code Quality Standards

### Coverage Gate

- Current coverage gate: **17%**
- Target: **25%** by Q2 2026
- Policy: Increase by +2% per PR when coverage exceeds gate

### Required CI Checks

All PRs must pass:
- `lint` - Pre-commit hooks and mypy
- `test` - pytest on Ubuntu + Windows (Python 3.10, 3.11)
- `install-smoke` - Package installation smoke test

### Hard Constraints

- ❌ No credentials, `.env.local`, SA JSON, or secrets in commits
- ❌ No network calls in tests (use mocks)
- ✅ Tests must pass on both Windows and Ubuntu

## Pre-commit Hooks

This repository uses pre-commit hooks organized in tiers:

### BLOCKING (run on every commit)
- Large file detection
- YAML syntax validation
- Secrets detection (detect-secrets)
- **Main branch block** - Prevents commits on `main`

### WARN_ONLY (run on push)
- Black formatting
- isort import sorting
- flake8 linting
- mypy type checking

## Getting Help

- Check existing issues and PRs
- Open an issue for bugs or feature requests
- Tag maintainers for urgent matters

---

**Maintainer:** @samiat-quadir
