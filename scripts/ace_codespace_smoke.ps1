
#Requires -Modules @{ ModuleName = 'Microsoft.PowerShell.Utility'; ModuleVersion = '1.0' }, @{ ModuleName = 'Microsoft.PowerShell.Core'; ModuleVersion = '7.0' }
#Requires -Version 7.0

$ErrorActionPreference = 'Stop'
$repo = 'samiat-quadir/bar-directory-recon'
$branch = git rev-parse --abbrev-ref HEAD

# Verify gh auth status
$authStatus = gh auth status -h github.com 2>&1
if ($authStatus -notmatch 'codespace') {
    Write-Output "SUMMARY >> task=ali_smoke_harden status=fail exit=1 note='gh auth missing codespace scope'"
    exit 1
}

# Create a throwaway Codespace
$codespaceName = (gh codespace create -R $repo -b $branch --machine standardLinux32gb --json "name" | ConvertFrom-Json).name
if (-not $codespaceName) {
    Write-Output "SUMMARY >> task=ali_smoke_harden status=fail exit=1 note='Failed to create codespace'"
    exit 1
}

try {
    # Wait until state=Available
    do {
        Start-Sleep -Seconds 10
        $codespaceState = (gh codespace view --codespace $codespaceName --json "state" | ConvertFrom-Json).state
    } while ($codespaceState -ne 'Available')

    # Copy smoke.sh to the codespace
    gh codespace cp scripts/smoke.sh "codespace:$codespaceName:/tmp/smoke.sh"
    if ($LASTEXITCODE -ne 0) {
        Write-Output "SUMMARY >> task=ali_smoke_harden status=fail exit=1 note='Failed to copy smoke.sh to codespace'"
        exit 1
    }

    # SSH to run the script
    $sshOutput = gh codespace ssh --codespace $codespaceName -- bash -lc 'dos2unix -q /tmp/smoke.sh || true; bash /tmp/smoke.sh; echo RUN_EXIT=$?'
    $exitCode = if ($sshOutput -match 'RUN_EXIT=(\d+)') { $matches[1] } else { 999 }
    $status = if ($exitCode -eq 0) { 'ok' } elseif ($exitCode -eq 1) { 'degraded' } else { 'fail' }

    # Capture last 40 lines
    $outputNote = $sshOutput.Split([Environment]::NewLine) | Select-Object -Last 40 | Out-String

    Write-Output "SUMMARY >> task=ali_smoke_harden status=$status exit=$exitCode note='$outputNote'"
}
finally {
    # Stop the Codespace
    gh codespace stop --codespace $codespaceName
}
