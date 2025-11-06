# Nov-6 GA Release Tasks Summary

**Status: READY FOR EXECUTION**  
**Decision Point: 09:30 ET (in progress)**

## 📋 Pre-Flight Checklist (Complete)

- ✅ **GA Gate Script Created**: `scripts/ops_ga_gate_execute.ps1`
- ✅ **Release Branch**: `release/0.1.1` exists with version bump
- ✅ **PR #312**: Draft GA gate PR ready (auto-merge OFF)
- ✅ **Smoke Test**: Completed Nov-5 (see `artifacts/rc1_windows_smoke.txt`)
- ⏳ **Workflows**: Need to verify publish-pypi.yml on main

## 🎯 Tasks Remaining Today

### 1. **Verify Workflow Files Exist** (PRIORITY: CRITICAL)

The publish-pypi.yml workflow may not be on main yet. Two options:

**Option A - Use existing files from branches:**
```powershell
# Copy workflows from remote branches
git show origin/ci/publish-pypi-manual-20251105-215901:.github/workflows/publish-pypi.yml > .github/workflows/publish-pypi.yml
git show origin/ci/insights-testpypi-line-20251104-174329:.github/workflows/insights-testpypi-line.yml > .github/workflows/insights-testpypi-line.yml

# Create PR for these files
git checkout -b ci/workflows-nov6-manual
git add .github/workflows/publish-pypi.yml .github/workflows/insights-testpypi-line.yml
git commit -m "ci: add production publish and insights workflows"
git push origin ci/workflows-nov6-manual
gh pr create --title "ci: add missing workflows for GA gate" --body "Adds publish-pypi.yml (manual production publish) and insights-testpypi-line.yml (weekly TestPyPI status)" --base main --auto-merge
```

**Option B - Run GA script (will fail fast if files missing):**
```powershell
# The script will check for files and exit with clear error if missing
pwsh -File scripts/ops_ga_gate_execute.ps1
```

### 2. **Execute GA Gate Script** (PRIORITY: CRITICAL)

Once workflows are confirmed on main:

```powershell
cd C:\Code\bar-directory-recon

# Dry-run to check all preconditions
pwsh -File scripts/ops_ga_gate_execute.ps1 -Version 0.1.1 -VersionTag v0.1.1 -GatePr 312

# If all checks pass, the script will:
# ✅ Verify gh CLI and repo path
# ✅ Check workflow files exist
# ✅ Verify PYPI_API_TOKEN secret
# ✅ Check parity run status (last run: Oct-30, SUCCESS)
# ✅ Check all 6 required checks on main
# ✅ Check cli-pack windows job success
# ✅ Dispatch publish-pypi workflow
# ✅ Poll until publish completes
# ✅ Update v0.1.1 release notes
# ✅ Comment on PR #312
```

### 3. **Monitor Publish Progress** (PASSIVE)

After script dispatches publish workflow:

```powershell
# Watch workflow progress
gh run list --workflow publish-pypi.yml --limit 1

# Check PyPI package appears
Start-Process "https://pypi.org/project/bar-directory-recon/0.1.1/"
```

### 4. **Finalize Release** (IF PUBLISH SUCCESS)

```powershell
# Convert PR #312 from draft
gh pr ready 312

# Merge PR #312
gh pr merge 312 --squash --delete-branch

# Verify main has v0.1.1
git pull origin main
grep "version = " pyproject.toml
```

## 🚨 IF ANY CHECKS FAIL

The script will exit with clear error. Do NOT publish. Instead:

```powershell
# Document failure on PR #312
gh pr comment 312 --body "⏸️ GA publish deferred on Nov-6 due to:

[Copy error message from script output]

Next review: [After fixes applied]"

# Investigate and fix issues
# Reschedule decision for later date
```

## 📊 Current Status

### Parity Check
- ✅ Latest run: Oct-30 (SUCCESS)
- URL: https://github.com/samiat-quadir/bar-directory-recon/actions/runs/18954051864

### Required Checks (Need Verification)
Need to check current status on main:
- audit
- fast-tests (ubuntu-latest)
- fast-tests (windows-latest)  
- workflow-guard
- ps-lint (ubuntu-latest)
- ps-lint (windows-latest)

### Workflows Status
- ✅ release-qa-parity.yml (exists on main)
- ✅ cli-pack.yml (exists on main)
- ⚠️ publish-pypi.yml (may need manual merge)
- ⚠️ insights-testpypi-line.yml (may need manual merge)

### Secrets
- ⏳ PYPI_API_TOKEN (needs verification, may need admin)

## 🔗 Key Links

- **PR #312**: https://github.com/samiat-quadir/bar-directory-recon/pull/312
- **Release v0.1.1**: https://github.com/samiat-quadir/bar-directory-recon/releases/tag/v0.1.1
- **Smoke Test Results**: `artifacts/rc1_windows_smoke.txt`
- **PyPI Package**: https://pypi.org/project/bar-directory-recon/ (will be 0.1.1 after publish)

## 📝 Decision Criteria

**PUBLISH IF:**
- ✅ Parity green
- ✅ All 6 required checks green
- ✅ Windows smoke passed (cli-pack)
- ✅ PYPI_API_TOKEN exists
- ✅ publish-pypi.yml exists on main

**DEFER IF:**
- ❌ Any check red/missing
- ❌ PYPI_API_TOKEN unavailable
- ❌ Workflows missing from main

## ⏰ Timeline

- **09:00-09:25 ET**: Verify workflows, run preflight checks
- **09:30 ET**: Execute GA gate script
- **09:30-10:00 ET**: Monitor publish workflow
- **10:00+ ET**: Finalize release (merge PR #312) or defer

---

**Generated**: Nov-6 2025  
**Purpose**: GA gate decision documentation  
**Next**: Execute Option A or B above
