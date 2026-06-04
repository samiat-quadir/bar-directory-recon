# CodeQL Security Scanning Setup

## Current Configuration

The `bar-directory-recon` project uses **Advanced CodeQL** analysis with the following setup:

- **File**: `.github/workflows/codeql-analysis.yml`
- **Trigger**: Push to main, PRs to main, weekly schedule (Monday 9 AM UTC)
- **Language**: Python
- **Query Suite**: `security-extended,security-and-quality`
- **Runner**: `ubuntu-latest`

## CodeQL Permissions

The CodeQL workflow requires:
- `contents: read` - To read the repository code
- `security-events: write` - To publish security events and code scanning results

## Disabling Default CodeQL Setup

GitHub provides a "Default setup" for CodeQL that may conflict with custom workflows.

### ⚠️ Important: Check Your Repository Settings

If both the **Advanced CodeQL workflow** (`.github/workflows/codeql-analysis.yml`) and **Default CodeQL setup** are active, they may:
- Create duplicate code scanning runs
- Cause "Expected" status checks in PRs
- Confuse CI/CD reporting

### How to Disable Default CodeQL Setup

1. **Navigate to Repository Settings**:
   - Go to: `https://github.com/samiat-quadir/bar-directory-recon/settings/security`
   - Click **Code security and analysis** (left sidebar)

2. **Find "Code QL"** section

3. **Disable "Default setup"**:
   - Look for **"Code QL setup"** or **"Code scanning: CodeQL"**
   - If "Default setup" is **Enabled** → Click to disable or uncheck it
   - Confirm: You want the **Advanced setup** only (via `.github/workflows/codeql-analysis.yml`)

4. **Verify**:
   - Confirm **only one** CodeQL configuration is active:
     - ❌ Default setup: DISABLED
     - ✅ Advanced setup (workflow file): ACTIVE

### Screenshots for Reference

**Step 1: Open Settings**

1. Repository → Settings (gear icon)
2. Code security and analysis

**Step 2: Locate CodeQL**

Look for "Code scanning" section, specifically "CodeQL".

**Step 3: Disable Default if Present**

If you see "Default" option next to CodeQL:
- Current status: [Enabled/Disabled]
- Click to toggle or use the dropdown to switch to None

**Step 4: Confirm Advanced Setup**

After disabling default:
- Verify your `.github/workflows/codeql-analysis.yml` is still committed
- It will serve as your sole CodeQL scanning source

## Verification Checklist

Use this checklist to confirm CodeQL is set up correctly:

```
CodeQL Setup Verification

Date: ________________
Verified by: ________________

WORKFLOW FILE:
[ ] .github/workflows/codeql-analysis.yml exists on main branch
[ ] Workflow triggers: push to main, PRs to main, weekly schedule
[ ] Query suites: security-extended, security-and-quality
[ ] Runs on: ubuntu-latest

GITHUB SETTINGS (https://github.com/samiat-quadir/bar-directory-recon/settings/security):
[ ] Code QL section available
[ ] Default setup: DISABLED or "None"
[ ] Advanced setup: ACTIVE (if visible in UI)

PR BEHAVIOR:
[ ] CodeQL check appears in PR status checks
[ ] CodeQL check status is "passing" or "pending" (never "expected")
[ ] No duplicate CodeQL checks in PR

OVERALL STATUS: ✅ or ❌
Notes: _________________________________________________________________
```

## Troubleshooting

### Issue: "Expected" CodeQL Check in PRs

**Cause**: Both default and advanced CodeQL setups are active.

**Solution**:
1. Open Settings → Code security and analysis
2. Disable "Default setup" for CodeQL
3. Keep `.github/workflows/codeql-analysis.yml` enabled

### Issue: CodeQL Workflow Not Running

**Possible Causes**:
1. Workflow file is deleted or has syntax error
2. Workflow is disabled in GitHub UI
3. File path is wrong (must be `.github/workflows/codeql-analysis.yml`)

**Solution**:
1. Verify file exists and is valid YAML
2. Check GitHub Actions tab for workflow errors
3. Manually trigger: Actions → CodeQL → Run workflow

### Issue: CodeQL Results Not Appearing

**Cause**: Incorrect permissions in workflow file.

**Solution**: Ensure the workflow has:
```yaml
permissions:
  contents: read
  security-events: write
```

## Security Event Publishing

CodeQL findings are published to the repository's **Security** tab:
- Navigate to: `https://github.com/samiat-quadir/bar-directory-recon/security`
- View: Code scanning results, alerts, and dismissals
- Configure: Scanning alert policies and notifications

## References

- GitHub CodeQL Documentation: https://docs.github.com/en/code-security/code-scanning/introduction-to-code-scanning/about-code-scanning-with-codeql
- Advanced Setup Guide: https://docs.github.com/en/code-security/code-scanning/creating-an-advanced-setup-for-code-scanning
- Default Setup Guide: https://docs.github.com/en/code-security/code-scanning/creating-an-advanced-setup-for-code-scanning/about-code-scanning-with-codeql-essentials

---

**Document Status**: Reference guide for CodeQL configuration verification.  
**Last Updated**: 2026-01-27
