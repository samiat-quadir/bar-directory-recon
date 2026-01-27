# Release Checklist

**Purpose**: Formalize the step-by-step process for releasing a new version of `bar-directory-recon`.

**Last Updated**: 2026-01-27  
**Version**: 1.0  

---

## Pre-Release Preconditions

Before beginning the release process, verify these conditions are met:

### 1. Repository Cleanliness
```powershell
# Main must be clean (no unstaged changes)
git status
# Expected: nothing to commit, working tree clean
```

- [ ] `git status` shows clean working directory on `main`
- [ ] No unmerged branches or uncommitted changes
- [ ] All temporary files committed or .gitignored

### 2. Required Checks Green (Pre-Release)

Verify that the latest commits on `main` pass all required automated checks:

```powershell
# Run locally (optional, but recommended)
python -m pytest --cov=src --cov=universal_recon --cov-fail-under=21
```

Required status checks on main (check GitHub Actions):
- [ ] ✅ `fast-tests` passing (Python 3.11, coverage >= gate)
- [ ] ✅ `lint` passing (ruff, mypy, flake8)
- [ ] ✅ `audit` passing (bandit, pip-audit)
- [ ] ✅ `ci-workflow-guard` passing (no unexpected workflow changes)

**Note**: If any check is failing, do NOT proceed. Fix the issue first.

### 3. Version Check

```powershell
python -c "import tomllib; import pathlib; print(tomllib.loads(pathlib.Path('pyproject.toml').read_text())['project']['version'])"
```

- [ ] Current version in `pyproject.toml` aligns with next release version
- [ ] Example: If releasing v0.1.7, ensure `version = "0.1.7"` in `pyproject.toml`

---

## Release Steps

### Step 1: Decide on Version Number

Determine the new release version using semantic versioning (MAJOR.MINOR.PATCH or MAJOR.MINOR.PATCH-prerelease).

Example versions:
- `0.1.7` — patch release (bug fix)
- `0.2.0` — minor release (new feature)
- `1.0.0` — major release (breaking change)

- [ ] Version decided and communicated to team
- [ ] Version follows semantic versioning

### Step 2: Update Version in pyproject.toml

Edit `pyproject.toml` and bump the version:

```toml
[project]
name = "bar-directory-recon"
version = "0.1.7"  # ← Update this to the release version
```

- [ ] `pyproject.toml` updated with new version
- [ ] No other version strings in the file (single source of truth)

### Step 3: Update CHANGELOG (if present)

If `CHANGELOG.md` exists, add an entry for the new release:

```markdown
## [0.1.7] - 2026-01-27

### Added
- Integrity: output collision prevention (UUID strategy)
- Integrity: empty-result fail-fast with configurable allow-empty

### Fixed
- Timezone: migrate all timestamps to UTC-aware

### Changed
- Coverage gate raised from 21% to 23%

### Security
- Dependency updates via pip-audit

[0.1.7]: https://github.com/samiat-quadir/bar-directory-recon/compare/v0.1.6...v0.1.7
```

- [ ] CHANGELOG.md updated (if file exists)
- [ ] Entry includes summary of major changes
- [ ] Comparison link added (v0.1.6...v0.1.7)

### Step 4: Run Full Test Suite Locally

```powershell
# Activate venv
.\.venv\Scripts\Activate.ps1

# Run full test suite
pytest -v

# Check coverage
pytest --cov=src --cov=universal_recon --cov-fail-under=21
```

- [ ] All tests pass locally
- [ ] Coverage meets or exceeds gate (21%)
- [ ] No new warnings or errors

### Step 5: Commit Version Bump (If Not Already Committed)

If version was not committed as part of a previous PR:

```powershell
git add pyproject.toml CHANGELOG.md  # If applicable
git commit -m "chore(release): bump version to 0.1.7"
git push origin main
```

- [ ] Version bump committed to main
- [ ] Push successful (no conflicts)

### Step 6: Tag the Release

```powershell
# Ensure you're on main and it's up-to-date
git checkout main
git pull origin main

# Create annotated tag
git tag -a v0.1.7 -m "Release 0.1.7"

# Verify tag created correctly
git show v0.1.7 --no-patch

# Push tag to origin
git push origin v0.1.7
```

- [ ] Tag `v0.1.7` created locally
- [ ] Tag pushed to GitHub (`origin`)
- [ ] Annotated tag verified with `git show`

### Step 7: Verify GitHub Release Artifacts

After pushing the tag, GitHub Actions automatically triggers the `release.yml` workflow.

Go to: https://github.com/samiat-quadir/bar-directory-recon/actions

Look for the `Release` workflow run triggered by your tag push:
1. Wait for workflow to complete (usually 2-5 minutes)
2. Check that all jobs passed:
   - [ ] `build` job: ✅ Passed
   - [ ] `install-smoke` job (ubuntu): ✅ Passed
   - [ ] `install-smoke` job (windows): ✅ Passed
   - [ ] `release` job: ✅ Passed

### Step 8: Verify GitHub Release Page

Go to: https://github.com/samiat-quadir/bar-directory-recon/releases

Look for the release corresponding to your tag (e.g., `v0.1.7`):

- [ ] Release page exists and is not a draft
- [ ] Release title: `Release 0.1.7` (or similar)
- [ ] Release notes populated (auto-generated or manually added)
- [ ] Assets attached:
  - [ ] `bar_directory_recon-0.1.7-py3-none-any.whl` (wheel)
  - [ ] `bar-directory-recon-0.1.7.tar.gz` (sdist/source distribution)
  - [ ] Both files have reasonable file sizes (not 0 bytes)

### Step 9: Verify Install-Smoke Test Results

In the release workflow run (Step 7), verify that install-smoke tests passed:

```
✅ ubuntu-latest: bdr --help passed, bdr doctor passed
✅ windows-latest: bdr --help passed, bdr doctor passed
```

- [ ] Install-smoke passed on ubuntu-latest
- [ ] Install-smoke passed on windows-latest
- [ ] Both logs show no ImportError or missing modules

### Step 10: Optional — Verify Artifacts Locally

For additional confidence, download and verify the wheel locally:

```powershell
# Download the .whl from GitHub Release
# Then:
mkdir .local-test-venv
python -m venv .local-test-venv
.local-test-venv\Scripts\Activate.ps1

# Install the downloaded wheel
pip install bar_directory_recon-0.1.7-py3-none-any.whl

# Test CLI
bdr --help
bdr doctor

# Clean up
deactivate
rmdir /s /q .local-test-venv
```

- [ ] Wheel installs without errors
- [ ] CLI commands execute successfully

---

## Troubleshooting

### Issue: Version Mismatch (pyproject.toml ≠ tag)

**Symptom**: Release workflow succeeded, but GitHub Release says v0.1.7 while pyproject.toml shows 0.1.6.

**Cause**: Version was not bumped in `pyproject.toml` before tagging.

**Fix**:
1. Do NOT tag again (tag already exists)
2. Bump version in `pyproject.toml` to match tag
3. Create a new commit: `chore(release): align version to 0.1.7`
4. Push to main
5. For next release, remember to bump version BEFORE tagging

### Issue: Missing Artifacts (No .whl or .tar.gz)

**Symptom**: GitHub Release page exists but has no attached files.

**Cause**: Usually means the `build` job failed or the `release` job didn't upload files.

**Fix**:
1. Check the `build` job logs in Actions:
   - Look for `python -m build` errors
   - Verify `twine check dist/*` passed
2. If build succeeded but upload failed:
   - Check `release` job logs for `upload-artifact` errors
   - Verify `softprops/action-gh-release` step succeeded
3. If all jobs passed but no artifacts:
   - Manually download artifacts from `build` job
   - Manually create/edit the GitHub Release and attach files

**Prevention**: Always verify CI logs before signing off.

### Issue: Install-Smoke Failure

**Symptom**: GitHub Release shows `install-smoke` job failed on ubuntu or windows.

**Cause**: Wheel has import errors, missing dependencies, or CLI is broken.

**Fix**:
1. Check the `install-smoke` logs in Actions:
   - Look for ImportError, ModuleNotFoundError
   - Look for CLI errors (e.g., `bdr: command not found`)
2. If import error:
   - Check that all dependencies are in `pyproject.toml`
   - Run `pip check` locally to verify dependency tree
   - Re-run release workflow (or retag if needed)
3. If CLI broken:
   - Test locally: `import bdr; bdr.cli.entrypoint()`
   - Check that `[project.scripts]` section in `pyproject.toml` is correct
   - Fix and create a hotfix PR, then re-release

**Prevention**: Always run `pytest` and `bdr --help` locally before tagging.

### Issue: GitHub Actions Permissions Error

**Symptom**: Release workflow fails with "Permission denied" for `contents: write`.

**Cause**: Workflow file is missing or malformed `permissions` block.

**Fix**:
1. Check `.github/workflows/release.yml`:
   - Must have `permissions: { contents: write }`
   - Must have `secrets.GITHUB_TOKEN` in `env`
2. If missing, add to workflow:
   ```yaml
   permissions:
     contents: write
   ```
3. Re-run workflow from Actions UI, or retag

**Prevention**: Reviewed in pre-release (check CI green).

### Issue: Conflicting Tag

**Symptom**: `git push origin v0.1.7` fails with "Tag already exists".

**Cause**: Tag was already pushed or created locally.

**Fix**:
1. Verify locally: `git tag -l | Select-String v0.1.7`
2. If tag exists but shouldn't:
   - Delete locally: `git tag -d v0.1.7`
   - Delete remote: `git push origin :refs/tags/v0.1.7`
   - Then re-create and push
3. If tag is correct:
   - No action needed; workflow already triggered

**Prevention**: Always verify with `git show v0.1.7 --no-patch` before pushing.

---

## Post-Release

### Update Documentation

- [ ] Add release badge/link to README.md (if applicable)
- [ ] Update any "Latest Release" references
- [ ] Close any release-related issues

### Communication

- [ ] Announce release in relevant channels (if applicable)
- [ ] Tag maintainers/contributors
- [ ] Share release notes link

### Monitoring

- [ ] Monitor for bug reports on the new release
- [ ] Watch CodeQL/security scans for any new findings
- [ ] Keep an eye on PyPI downloads (if released to PyPI)

---

## Release Cadence & Planning

| Release | Target Date | Type | Notes |
|---------|-------------|------|-------|
| v0.1.6 | 2026-01-27 | Patch | Version alignment + release workflow fix |
| v0.1.7 | 2026-02-15 | Minor | Integrity gap enforcement (5 PRs merged) |
| v0.2.0 | 2026-Q2 | Minor | Next feature batch |
| v1.0.0 | 2026-Q3 | Major | Production release candidate |

**Note**: Dates are estimates. Actual releases depend on PR completion and testing.

---

## Quick Reference Commands

```powershell
# Pre-release checks
git status
pytest --cov=src --cov=universal_recon --cov-fail-under=21

# Update version
# (Edit pyproject.toml manually)

# Commit and tag
git add pyproject.toml CHANGELOG.md
git commit -m "chore(release): bump version to 0.1.7"
git tag -a v0.1.7 -m "Release 0.1.7"
git push origin main
git push origin v0.1.7

# Verify tag
git show v0.1.7 --no-patch

# Watch CI
# (GitHub Actions → Release workflow)

# Verify artifacts
# (https://github.com/samiat-quadir/bar-directory-recon/releases)
```

---

**For questions or issues with the release process, contact the repo maintainer.**
