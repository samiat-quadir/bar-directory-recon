# Pre-commit Cache Corruption Fix Guide

## Issue Summary
Pre-commit hooks can fail with "InvalidManifestError" due to Windows permission issues in the cache directory.

## Error Pattern
```
InvalidManifestError:

=====> C:\Users\[user]\.cache\pre-commit\repo[id]\.pre-commit-hooks.yaml is not a file
```

## Quick Fix
```powershell
# Option 1: Use the automated script
.\fix_precommit_cache.ps1 -Force

# Option 2: Manual fix
takeown /f "$env:USERPROFILE\.cache\pre-commit" /r /d y
icacls "$env:USERPROFILE\.cache\pre-commit" /grant "$env:USERNAME`:F" /t
Remove-Item "$env:USERPROFILE\.cache\pre-commit" -Recurse -Force

# Option 3: Bypass for urgent commits
git commit --no-verify -m "Your message"
```

## Prevention
1. **Run as Administrator**: Run VS Code/PowerShell as administrator when doing heavy git operations
2. **Regular Cache Cleanup**: Periodically clear pre-commit cache: `pre-commit clean`
3. **Virtual Environment**: Use virtual environments to isolate pre-commit installations

## Permanent Solutions
1. **Update Pre-commit**: Ensure latest version with `pip install --upgrade pre-commit`
2. **Repository-specific Install**: Use `pre-commit install --install-hooks` in each repo
3. **Cache Location**: Consider moving cache to a location without permission issues

## Files Created
- `fix_precommit_cache.ps1` - Automated fix script
- This guide for future reference

## When to Use Each Option
- **Automated Script**: Regular development workflow
- **Manual Commands**: When script fails or debugging needed
- **--no-verify**: Emergency commits when hooks are broken
- **Clean Reinstall**: When corruption is persistent

---
**Last Updated**: August 18, 2025
**Status**: ✅ Issue resolved - DevContainer implementation complete