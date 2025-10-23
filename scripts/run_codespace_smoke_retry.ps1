Param()
$ErrorActionPreference = 'Stop'
Set-Location -Path "C:\Code\bar-directory-recon"

# Hector's robust Codespace smoke script: 2 retries, map displayName->name, poll until Available, run pytest, then stop
function New-Smoke {
    param(
        [string]$Branch
    )
    $displayName = 'bdr-smoke-' + ([System.Guid]::NewGuid().ToString('N').Substring(0, 6))
    # Create codespace quietly
    gh codespace create -R samiat-quadir/bar-directory-recon -b $Branch -m standardLinux32 --idle-timeout 45m --retention-period 1day --display-name $displayName --default-permissions *> $null

    # Map displayName -> name (poll until we get a name or timeout)
    $name = $null
    $tries = 0
    do {
        Start-Sleep -Seconds 8
        try {
            $json = gh codespace list --json name, displayName, state, repository 2>$null | ConvertFrom-Json
            if ($json) {
                $entry = $json | Where-Object { $_.displayName -eq $displayName -and ($_.repository -like '*bar-directory-recon*') }
                if ($entry) { $name = $entry.name }
            }
        }
        catch { }
        $tries++
    } while (-not $name -and $tries -lt 20)

    if (-not $name) { return @{ ok = $false; reason = 'no_name_after_poll'; display = $displayName } }

    # Wait for state == Available
    $state = $null
    $tries = 0
    do {
        Start-Sleep -Seconds 6
        try {
            $json = gh codespace list --json name, state 2>$null | ConvertFrom-Json
            $state = ($json | Where-Object { $_.name -eq $name }).state
        }
        catch { }
        $tries++
    } while ($state -ne 'Available' -and $tries -lt 30)

    if ($state -ne 'Available') {
        try { gh codespace stop -c $name *> $null } catch { }
        return @{ ok = $false; reason = 'not_available'; name = $name; display = $displayName }
    }

    # Run pytest inside the codespace devcontainer and capture the last line
    $tail = $null
    try {
        $tail = gh codespace ssh -c $name -- 'bash -lc "pytest -q -k \"not slow and not e2e and not integration\" 2>&1 | tail -n 1"' 2>$null
    }
    catch {
        $tail = "SSH_OR_PYTEST_ERROR: $($_.Exception.Message)"
    }

    # Stop the codespace
    try { gh codespace stop -c $name *> $null } catch { }

    return @{ ok = $true; name = $name; tail = $tail; display = $displayName }
}

# Determine branch to use (prefer current local branch)
$branch = 'main'
if (Test-Path .git) {
    try { $b = (git rev-parse --abbrev-ref HEAD).Trim(); if ($b) { $branch = $b } } catch { }
}

$attempt = 0
$res = $null
while ($attempt -lt 2 -and (-not $res -or -not $res.ok)) {
    $attempt++
    $res = New-Smoke -Branch $branch
}

if (-not $res.ok) {
    Write-Host 'UI_FALLBACK_REQUIRED'
    Write-Host 'Open the repo on GitHub → Code → Codespaces → “Create codespace on main” → once green, run a rebuild in the UI, then say: READY'
    Write-Output "SUMMARY >> task=ace_codespaces status=fail need_ui=true note=$($res.reason) display=$($res.display)"
    exit 0
}
else {
    $status = (($res.tail -match 'passed') -and ($res.tail -notmatch 'FAILED|ERROR')) ? 'ok' : 'degraded'
    Write-Output "SUMMARY >> task=ace_codespaces status=$status need_ui=false cs_name=$($res.name) tail='$($res.tail)'"
}
