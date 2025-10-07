# Smoke test script to trigger ps-lint and validate composite guard integration
# This script will be removed after successful validation

Write-Host "🧪 Smoke test: Composite guard integration"
Write-Host "✅ This triggers ps-lint to validate guard workflow changes"
Write-Host "⚡ Testing branch protection with 4 required status checks:"
Write-Host "   1. audit"
Write-Host "   2. fast-tests (ubuntu-latest)"
Write-Host "   3. fast-tests (windows-latest)"
Write-Host "   4. workflow-guard (if applicable)"

# Validate that composite guard action exists
if (Test-Path ".github/actions/guard/action.yml") {
    Write-Host "✅ Composite guard action found"
} else {
    Write-Host "❌ Composite guard action missing"
    exit 1
}

# Check that workflows reference the composite action
$workflows = @(".github/workflows/fast-parity-ci.yml", ".github/workflows/pip-audit.yml")
foreach ($workflow in $workflows) {
    if (Test-Path $workflow) {
        $content = Get-Content $workflow -Raw
        if ($content -match "uses: \./\.github/actions/guard") {
            Write-Host "✅ $workflow uses composite guard"
        } else {
            Write-Host "❌ $workflow missing composite guard reference"
        }
    }
}

Write-Host "🎯 Smoke test complete - PR should trigger all required checks"