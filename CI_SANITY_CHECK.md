# CI Sanity Check - October 2, 2025

This file tests the attic/CI sanity monitoring to ensure:

1. **Exactly three required checks** run on PRs:
   - fast-tests (ubuntu-latest) ✅ 
   - fast-tests (windows-latest) ✅
   - audit ✅

2. **Guard workflow** runs but is **non-required**
   - workflow-guard ✅ (should pass since no workflow changes)

3. **PS-lint** should **NOT appear** (no scripts/** changes)

4. **Other workflows** may run but should be **non-required**

## Expected Results:
- 3 required status checks (green)
- Guard passes (non-required)
- PS-lint absent (path-filtered out)
- Total Actions workflows: various non-required ones

## Test Change:
Adding this documentation file to trigger CI without touching workflows or scripts.