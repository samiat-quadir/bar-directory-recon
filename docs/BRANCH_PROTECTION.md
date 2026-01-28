# [DEPRECATED] Branch Protection Rules — Main Branch

> [!IMPORTANT]  
> This file is **deprecated** and kept only for historical reference.  
> The **authoritative branch protection documentation** is in `docs/branch-protection.md`.

**Purpose**: Historical snapshot of branch protection rules for the `main` branch (non-authoritative).

**Last Verified**: 2026-01-27  
**Status**: DEPRECATED — SEE `docs/branch-protection.md`  

---

## Required Protection Rules for `main`

All rules below **MUST be enabled** to protect the main branch from accidental or malicious changes.

### A. Basic Protections

| Rule | Expected | Verified |
|------|----------|----------|
| ✅ Require a PR before merge | YES | ⏳ |
| ✅ Require status checks to pass before merge | YES | ⏳ |
| ✅ Require branches to be up to date before merge | YES | ⏳ |
| ✅ Restrict who can push to matching branches | YES | ⏳ |
| ✅ Allow force pushes | NO (disabled) | ⏳ |
| ✅ Allow deletions | NO (disabled) | ⏳ |

### B. Required Status Checks (CI Gates)

These checks **MUST pass** before any PR can merge to main:

| Check | Expected | Owner | Notes |
|-------|----------|-------|-------|
| `fast-tests (ubuntu)` | REQUIRED | GitHub Actions | Python pytest on Ubuntu |
| `fast-tests (windows)` | REQUIRED | GitHub Actions | Python pytest on Windows |
| `audit (ubuntu)` | REQUIRED | GitHub Actions | Bandit + pip-audit (Ubuntu only) |
| `workflow-guard (ubuntu)` | REQUIRED | GitHub Actions | No unexpected workflow changes (Ubuntu only) |
| `fast-tests (ubuntu)` | REQUIRED | GitHub Actions | Python environment & package installation validation on Ubuntu |
| `fast-tests (windows)` | REQUIRED | GitHub Actions | Python environment & package installation validation on Windows |
| `audit` | REQUIRED | GitHub Actions | Bandit + pip-audit (ubuntu-latest only; single `audit` status check) |
| `workflow-guard` | REQUIRED | GitHub Actions | No unexpected workflow changes (ubuntu-latest only; single `workflow-guard` status check) |
| `workflow-guard` | REQUIRED | GitHub Actions | No unexpected workflow changes (single check running on `ubuntu-latest`) |
| `ps-lint (ubuntu)` | REQUIRED | GitHub Actions | PowerShell linting on Ubuntu |
| `ps-lint (windows)` | REQUIRED | GitHub Actions | PowerShell linting on Windows |
| `install-smoke (ubuntu)` | REQUIRED | GitHub Actions | Wheel install + CLI smoke test (Ubuntu) |
| `install-smoke (windows)` | REQUIRED | GitHub Actions | Wheel install + CLI smoke test (Windows) |

### C. Admin Bypass

| Rule | Expected | Verified |
|------|----------|----------|
| ✅ Dismiss stale pull request approvals when new commits are pushed | YES (enabled) | ⏳ |
| ✅ Require code owner review | YES (if CODEOWNERS exists) | ⏳ |
| ✅ Allow admins to bypass required status checks | NO (disabled) | ⏳ |

### D. Secret Scanning

| Feature | Expected | Verified |
|---------|----------|----------|
| ✅ Secret scanning enabled | YES | ⏳ |
| ✅ Push protection enabled | YES | ⏳ |
| ✅ Web UI alerts enabled | YES | ⏳ |

---

## How to Verify Branch Protection Rules

### Step 1: Navigate to Settings

1. Go to: https://github.com/samiat-quadir/bar-directory-recon
2. Click **Settings** (top right, gear icon)
3. Click **Branches** (left sidebar)

### Step 2: Check Rule 1 — Require PR Before Merge

Under "Branch protection rules" → **main**:

- [ ] ✅ "Require a pull request before merging" is **checked**
- [ ] ✅ "Require approvals" is set to at least **1**
- [ ] ✅ "Require code owner reviews" is checked (if applicable)
- [ ] ✅ "Dismiss stale pull request approvals when new commits are pushed" is **checked**

**Expected state**: PR required, at least 1 approval, auto-dismiss on new commits

### Step 3: Check Rule 2 — Require Status Checks

Under same rule → scroll to "Require status checks to pass before merging":

- [ ] ✅ "Require branches to be up to date before merge" is **checked**
- [ ] ✅ All 5 required status checks (running across 8 job instances) are listed and **selected**:
  - `fast-tests (ubuntu)`
  - `fast-tests (windows)`
  - `audit` (ubuntu-only, no Windows variant)
  - `workflow-guard` (ubuntu-only, no Windows variant)
  - `ps-lint (ubuntu)`
  - `ps-lint (windows)`
  - `install-smoke (ubuntu)`
  - `install-smoke (windows)`

**Expected state**: All 5 status checks (8 job instances total) required and green before merge

### Step 4: Check Rule 3 — Disable Force Pushes & Deletions

Same rule → scroll to bottom:

- [ ] ✅ "Allow force pushes" is **NOT checked** (disabled)
- [ ] ✅ "Allow deletions" is **NOT checked** (disabled)
- [ ] ✅ "Allow bypassing the above settings for administrators" is **NOT checked** (disabled)

**Expected state**: Force pushes blocked, deletions blocked, no admin bypass

### Step 5: Check Secret Scanning

1. Go to **Settings** → **Code security and analysis**
2. Scroll to "Secret scanning":
   - [ ] ✅ "Secret scanning" is **Enabled**
   - [ ] ✅ "Push protection" is **Enabled**

**Expected state**: Both enabled

---

## Verification Checklist

Copy this checklist and fill it out:

```
Branch Protection Verification — main

Date: ________________
Verified by: ________________

BASIC PROTECTIONS:
[ ] Require PR before merge: YES
[ ] Require status checks: YES
[ ] Require up-to-date branches: YES
[ ] Restrict push access: YES
[ ] Force pushes: DISABLED
[ ] Deletions: DISABLED

REQUIRED STATUS CHECKS (5 checks, 8 job instances):
[ ] fast-tests (ubuntu): REQUIRED
[ ] fast-tests (windows): REQUIRED
[ ] audit: REQUIRED (ubuntu-only, no Windows variant)
[ ] workflow-guard: REQUIRED (ubuntu-only, no Windows variant)
[ ] ps-lint (ubuntu): REQUIRED
[ ] ps-lint (windows): REQUIRED
[ ] install-smoke (ubuntu): REQUIRED
[ ] install-smoke (windows): REQUIRED

Note: audit and workflow-guard also run as required checks but only on ubuntu-latest
[ ] audit: REQUIRED (ubuntu-latest only; no platform variants)
[ ] workflow-guard: REQUIRED (ubuntu-latest only; no platform variants)

ADMIN BYPASS:
[ ] Stale approval dismissal: YES
[ ] Code owner review: YES (if CODEOWNERS exists)
[ ] Admin bypass: DISABLED

SECRET SCANNING:
[ ] Secret scanning enabled: YES
[ ] Push protection enabled: YES

OVERALL STATUS: [ ] PASS [ ] FAIL [ ] PARTIAL

Notes:
_______________________________________________________________________
```

---

## If Verification FAILS

If any rule is missing or incorrectly configured:

1. **Do NOT proceed** with any merges until rules are fixed
2. Contact the repo maintainer (samiat-quadir)
3. Provide the filled-out verification checklist
4. Document which specific rules are missing/incorrect

---

## How to Configure (If Missing)

If any rules are missing, here's the configuration order:

1. Go to **Settings** → **Branches**
2. Click **Add rule** or edit **main** rule
3. Enable rules in this order:
   - Basic protections (PR, status checks, up-to-date)
   - Require all 5 status checks from CI (8 job instances total)
   - Disable force pushes and deletions
   - Disable admin bypass
4. Click **Save changes**
5. Re-verify using the checklist above

---

## Why These Rules?

| Rule | Benefit |
|------|---------|
| **Require PR** | No direct commits to main; all changes reviewed |
| **Require status checks** | CI gates prevent broken code merges |
| **Require up-to-date** | Prevents stale branch merges with race conditions |
| **No force pushes** | Prevents history rewriting on main |
| **No admin bypass** | Enforces gate rules for all contributors, including maintainers |
| **Secret scanning** | Prevents credentials from being committed |

---

## Post-Verification

Once all rules are verified as **PASS**:

- [ ] Update this document with verification date
- [ ] Confirm with team that main is protected
- [ ] Document in release/operational runbook

**If FAIL**: Create an issue with the missing rules and assign to maintainer.

---

## References

- GitHub Docs: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches
- Security: https://docs.github.com/en/code-security/secret-scanning/about-secret-scanning

---

**Document Status**: Ready for verification by repo maintainer (samiat-quadir).
