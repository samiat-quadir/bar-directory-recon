
#Requires -Modules @{ ModuleName = 'Microsoft.PowerShell.Utility'; ModuleVersion = '1.0' }, @{ ModuleName = 'Microsoft.PowerShell.Core'; ModuleVersion = '7.0' }
#Requires -Version 7.0

$ErrorActionPreference = 'Stop'
$repo = 'samiat-quadir/bar-directory-recon'
$targetRef = git rev-parse --abbrev-ref HEAD
$codespaceDisplayName = "bdr-smoke-$(Get-Date -Format yyyyMMdd-HHmm)"

# Verify gh auth status
$authStatus = gh auth status -h github.com 2>&1
if ($authStatus -notmatch 'codespace') {
    Write-Output "SUMMARY >> task=ali_smoke_wrap status=fail exit=1 note='gh auth missing codespace scope'"
    
    exit 1
}

# Create a throwaway Codespace
$codespaceJson = gh codespace create -R $repo -b $targetRef -m standardLinux32gb --display-name $codespaceDisplayName --json "name"
$codespaceName = ($codespaceJson | ConvertFrom-Json).name
if (-not $codespaceName) {
    Write-Output "SUMMARY >> task=ali_smoke_wrap status=fail exit=1 note='Failed to create codespace'"

    exit 1
}

try {
    # Wait until state=Available
    do {
        Start-Sleep -Seconds 10
        $codespaceState = (gh codespace list --json "name,state" | ConvertFrom-Json | Where-Object { $_.name -eq $codespaceName }).state
    } while ($codespaceState -ne 'Available')

    # SSH to run the script
    $sshOutput = gh codespace ssh -c $codespaceName -- bash -lc 'cat > /tmp/smoke.sh << "SH"
#!/usr/bin/env bash
set -Eeuo pipefail
cd "/workspaces/bar-directory-recon"
dos2unix -q scripts/smoke.sh || true
bash scripts/smoke.sh
SH
chmod +x /tmp/smoke.sh && bash /tmp/smoke.sh; echo RUN_EXIT=$?'
    
    $exitCode = if ($sshOutput -match 'RUN_EXIT=(\d+)') { $matches[1] } else { 999 }
    $status = if ($exitCode -eq 0) { 'ok' } elseif ($exitCode -eq 1) { 'degraded' } else { 'fail' }

    # Capture last 40 lines
    $outputNote = $sshOutput.Split([Environment]::NewLine) | Select-Object -Last 40 | Out-String

    Write-Output "SUMMARY >> task=ali_smoke_wrap status=$status exit=$exitCode note='$outputNote'"
}
finally {
    # Stop the Codespace
    gh codespace stop -c $codespaceName
}
