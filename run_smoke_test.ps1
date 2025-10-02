#!/usr/bin/env pwsh

$ErrorActionPreference = "Stop"
$timestamp = Get-Date -Format "yyyyMMdd-HHmm"
$random = -join ((48..57) + (97..122) | Get-Random -Count 16 | ForEach-Object { [char]$_ })
$cs_name = "bdr-ace-smoke-$timestamp-$random"
$branch = "feat/legacy-adapter-refactor" # Using the current branch
$status = "init"
$exit = ""
$testResults = ""

Write-Output "Creating codespace for branch $branch..."

try {
    # Create the codespace and capture the name
    $createOutput = gh codespace create --repo samiat-quadir/bar-directory-recon --branch $branch --machine basicLinux32gb

    # Extract codespace name from the last line of output
    $cs_name = $createOutput | Select-Object -Last 1
    Write-Output "Created codespace: $cs_name"

    # Wait for the codespace to be ready - poll status
    $ready = $false
    $retries = 0
    $maxRetries = 20

    do {
        Start-Sleep -Seconds 10
        $retries++
        Write-Output "Checking codespace status (attempt $retries/$maxRetries)..."

        $cs_list = gh codespace list --json name, state
        if ($cs_list -match "`"name`":\s*`"$cs_name`",\s*`"state`":\s*`"Available`"") {
            $ready = $true
            Write-Output "Codespace is available!"
        }

        if ($retries -ge $maxRetries) {
            throw "Timeout waiting for codespace to be ready"
        }
    } while (-not $ready)

    Write-Output "Codespace is ready. Running smoke test..."

    # Phase 1: Create the smoke_test.sh script in the codespace
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
else
    echo "====================== SMOKE TEST FAILED ======================"
    exit $TEST_EXIT
fi

echo "Smoke test completed successfully!"
'@

    # Use SSH to create the script file by creating a local file and transferring it
    $temp_script_path = Join-Path $env:TEMP "smoke_test.sh"
    Set-Content -Path $temp_script_path -Value $script_content

    # Upload the script to the codespace
    gh codespace cp $temp_script_path "remote:/home/codespace/smoke_test.sh" -c $cs_name

    # Set permissions
    gh codespace ssh -c "chmod +x ~/smoke_test.sh" $cs_name

    # Clean up the temporary file
    Remove-Item -Path $temp_script_path

    # Phase 2: Execute the script
    Write-Output "Executing smoke test in codespace $cs_name..."
    $testOutput = gh codespace ssh --codespace $cs_name -c "cd /workspaces/bar-directory-recon && bash ~/smoke_test.sh"
    $testResults = $testOutput -join "`n"

    # Check if smoke test passed
    if ($testResults -match "SMOKE TEST PASSED") {
        $status = "pass"
        Write-Output "Smoke test passed!"
    }
    else {
        $status = "fail"
        Write-Output "Smoke test failed!"

        # Extract exit code if available
        if ($testResults -match "TEST_EXIT=(\d+)") {
            $exit = $matches[1]
        }
    }
}
catch {
    $status = "error"
    $exit = $_.Exception.Message
    Write-Output "Error: $_"
}
finally {
    # Output summary
    Write-Output ""
    Write-Output "SUMMARY >> task=ace_inline_smoke status=$status exit=$exit cs=$cs_name ref='$branch' tail='$testResults'"

    # Optional: Delete the codespace if needed
    # Write-Output "Cleaning up codespace..."
    # gh codespace delete -c $cs_name --force
}
