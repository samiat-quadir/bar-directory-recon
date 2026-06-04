# Branch Protection Setup Guide

This document provides step-by-step instructions for configuring branch protection rules on GitHub for the `main` branch.

## Prerequisites

- Repository admin access on GitHub
- Repository: `samiat-quadir/bar-directory-recon`

## Steps to Enable Branch Protection

### 1. Navigate to Branch Protection Settings

1. Go to https://github.com/samiat-quadir/bar-directory-recon
2. Click **Settings** (gear icon in the top menu)
3. In the left sidebar, click **Branches** under "Code and automation"
4. Click **Add branch protection rule** (or edit existing rule for `main`)

### 2. Configure the Branch Pattern

- **Branch name pattern:** `main`

### 3. Required Settings (BLOCKING)

Enable these protection rules:

#### ✅ Require a pull request before merging
- Check: **Require a pull request before merging**
- Check: **Require approvals** → Set to `1` (recommended)
- Optional: **Dismiss stale pull request approvals when new commits are pushed**

#### ✅ Require status checks to pass before merging
- Check: **Require status checks to pass before merging**
- Check: **Require branches to be up to date before merging**
- Add these required status checks:
  - `lint`
  - `test (3.11, ubuntu-latest)`
  - `test (3.11, windows-latest)`
  - `install-smoke (ubuntu-latest)`
  - `install-smoke (windows-latest)`

#### ✅ Block force pushes
- Check: **Do not allow force pushes**

#### ✅ Block deletions
- Check: **Do not allow deletions**

### 4. Optional but Recommended

#### Require conversation resolution
- Check: **Require conversation resolution before merging**

#### Restrict who can push
- Check: **Restrict who can push to matching branches**
- Add only trusted maintainers or leave empty to enforce PR-only workflow

### 5. Save the Rule

Click **Create** (or **Save changes** if editing)

## Verification

After enabling branch protection:

1. Try pushing directly to main:
   ```bash
   git checkout main
   echo "test" >> test.txt
   git add test.txt
   git commit -m "test"
   git push origin main
   ```
   
   **Expected:** Push should be rejected with an error about required pull request.

2. Verify status checks are required:
   - Open any PR targeting `main`
   - Confirm merge is blocked until all required checks pass

## Local Pre-commit Hook

In addition to GitHub branch protection, this repository includes a local pre-commit hook that blocks commits on `main` before they even happen. See `.pre-commit-config.yaml` for configuration.

## Troubleshooting

### "Required status check is expected" but check never runs

Ensure the status check names match exactly what's in the CI workflow. Check names are case-sensitive.

### Force push needed for emergency fix

1. Temporarily disable the "Do not allow force pushes" rule
2. Make the emergency fix
3. Re-enable the rule immediately
4. Document the incident

---

**Last Updated:** January 2026
**Maintainer:** @samiat-quadir
