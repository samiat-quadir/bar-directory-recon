# Test script to trigger ps-lint workflow
# This is a minimal PowerShell script to test the path-filtered ps-lint workflow

Write-Host "PS-lint workflow test triggered on $(Get-Date)"
Write-Host "This script exercises the ps-lint path filter for scripts/**"

# No-op function to provide some PowerShell content for analysis
function Test-PSLintWorkflow {
    param(
        [string]$TestMessage = "PS-lint path filter working correctly"
    )
    
    Write-Output $TestMessage
    return $true
}

# Call the test function
Test-PSLintWorkflow -TestMessage "Testing ps-lint on both Ubuntu and Windows runners"