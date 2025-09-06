#!/usr/bin/env pwsh

$ErrorActionPreference = "Stop"
$branch = "feat/legacy-adapter-refactor"
$timestamp = Get-Date -Format "yyyyMMdd-HHmm"
$codespace_name = ""

Write-Output "========== SMOKE TEST START =========="
Write-Output "Branch: $branch"
Write-Output "Date: $timestamp"

# First check for and delete old codespaces if needed
Write-Output "Checking for existing codespaces..."
$existing = gh codespace list --json name, state, repository | ConvertFrom-Json
$running_count = ($existing | Where-Object { $_.state -eq "Available" }).Count

if ($running_count -ge 3) {
    Write-Output "Found $running_count running codespaces. Cleaning up old ones..."
    $oldest = $existing | Where-Object { $_.state -eq "Available" } | Select-Object -First 2
    foreach ($cs in $oldest) {
        Write-Output "Deleting codespace $($cs.name)..."
        gh codespace delete -c $cs.name -f
    }
}

Write-Output "Creating codespace for branch $branch..."

try {
    # Create the codespace
    $output = gh codespace create --repo samiat-quadir/bar-directory-recon --branch $branch --machine basicLinux32gb
    $codespace_name = $output | Select-Object -Last 1
    Write-Output "Created codespace: $codespace_name"

    # Loop to check status
    $codespace_ready = $false
    for ($i = 1; $i -le 20; $i++) {
        Write-Output "Checking status (attempt $i/20)..."
        Start-Sleep -Seconds 10
        
        # Simple approach - just list all codespaces and check if any are available
        $list_output = gh codespace list
        if ($list_output -match $codespace_name -and $list_output -match "Available") {
            Write-Output "Codespace is ready!"
            $codespace_ready = $true
            break
        }
    }

    if (-not $codespace_ready) {
        throw "Timed out waiting for codespace to be ready"
    }
    
    # Create the test script
    $script_content = @'
#!/bin/bash
set -e
echo "====================== SMOKE TEST START ======================"
echo "Running smoke test in codespace..."

# Checkout the correct branch and update
git checkout feat/legacy-adapter-refactor || echo "Failed to checkout branch"
git pull || echo "Failed to pull latest changes"

# Check Python version and environment
echo "Python version:"
python --version
which python

# Install dependencies
if [ -f .devcontainer/setup.sh ]; then
    echo "Running .devcontainer/setup.sh..."
    bash .devcontainer/setup.sh
fi

# Install test requirements
echo "Installing test requirements..."
python -m pip install -r requirements-test.txt || echo "No requirements-test.txt found or installation failed"

# Run a specific test as a smoke test
# pragma: allowlist-secret special-exclude-case
echo "Running pytest smoke tests..."
TEST_EXIT=0
python -m pytest -v tests/adapters/test_collab_divorce_adapter.py::test_extract_emails_from_text || TEST_EXIT=$?
echo "TEST_EXIT=${TEST_EXIT}"

if [ $TEST_EXIT -eq 0 ]; then
    echo "====================== SMOKE TEST PASSED ======================"
    exit 0
else
    echo "====================== SMOKE TEST FAILED ======================"
    exit $TEST_EXIT
fi
'@
    
    # Use SSH to create the script file
    $temp_script_path = Join-Path $env:TEMP "smoke_test.sh"
    Set-Content -Path $temp_script_path -Value $script_content
    
    # Upload the script to the codespace
    Write-Output "Uploading test script..."
    gh codespace cp -c $codespace_name $temp_script_path "remote:/workspaces/bar-directory-recon/smoke_test.sh"
    
    # Set execute permissions
    Write-Output "Setting execute permissions..."
    gh codespace ssh -c $codespace_name -- "chmod +x /workspaces/bar-directory-recon/smoke_test.sh"
    
    # Remove temp file
    Remove-Item -Path $temp_script_path -Force
    
    # Execute the script
    Write-Output "Running smoke test..."
    $test_result = gh codespace ssh -c $codespace_name -- "cd /workspaces/bar-directory-recon && ./smoke_test.sh"
    
    # Check for success - look for RUN_EXIT=0 which indicates the pytest tests passed
    if ($test_result -match "RUN_EXIT=0") {
        Write-Output "========== SMOKE TEST SUCCEEDED =========="
        $test_result | ForEach-Object { Write-Output $_ }
        Write-Output "SUMMARY >> task=ace_inline_smoke status=pass exit=0 cs=$codespace_name ref='$branch'"
    }
    else {
        Write-Output "========== SMOKE TEST FAILED =========="
        $test_result | ForEach-Object { Write-Output $_ }
        
        # Extract exit code if available
        $exit_code = "1"
        if ($test_result -match "TEST_EXIT=(\d+)") {
            $exit_code = $matches[1]
        }
        elseif ($test_result -match "RUN_EXIT=(\d+)") {
            $exit_code = $matches[1]
        }
        
        Write-Output "SUMMARY >> task=ace_inline_smoke status=fail exit=$exit_code cs=$codespace_name ref='$branch'"
    }
}
catch {
    Write-Output "========== SMOKE TEST ERROR =========="
    Write-Output "Error: $_"
    Write-Output "SUMMARY >> task=ace_inline_smoke status=error exit=$($_.Exception.Message) cs=$codespace_name ref='$branch'"
}
finally {
    # Clean up the codespace if it was created
    if ($codespace_name) {
        Write-Output "Cleaning up codespace..."
        try {
            gh codespace delete -c $codespace_name -f
            Write-Output "Codespace deleted."
        }
        catch {
            Write-Output "Failed to delete codespace: $_"
        }
    }
}