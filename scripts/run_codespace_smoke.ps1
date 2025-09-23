Param()
$ErrorActionPreference = 'Stop'
Set-Location -Path "C:\Code\bar-directory-recon"

# 1) Check GitHub CLI auth & scopes
$status = (gh auth status 2>&1 | Out-String)
$hasCodespace = $status -match 'Token scopes:.*codespace'
if (-not $hasCodespace) {
    Write-Host "ACTION_NEEDED: Run 'gh auth refresh -h github.com -s codespace -s repo -s workflow' on this machine, complete browser flow, then re-run."
    Write-Output "SUMMARY >> task=ace_health_codespace status=blocked reason=missing_scope"
    exit 0
}

# 2) Pick branch: prefer the current local branch (so recent devcontainer changes are used), fallback to 'main'
try {
    $branch = (git rev-parse --abbrev-ref HEAD).Trim()
    if (-not $branch) { $branch = 'main' }
    # ensure the branch exists remotely; fallback to main if not
    git ls-remote --exit-code origin $branch > $null
    if ($LASTEXITCODE -ne 0) { $branch = 'main' }
}
catch {
    $branch = 'main'
}

# 3) Create ephemeral Codespace (use 24h retention)
$name = "bdr-smoke-$([System.Guid]::NewGuid().ToString('N').Substring(0,6))"
# Create codespace (async). We'll poll for the real codespace name.
gh codespace create -R samiat-quadir/bar-directory-recon -b $branch -m "standardLinux32gb" --idle-timeout "60m" --retention-period "24h" --display-name $name --default-permissions

# Poll for codespace entry (the API may return a short name); give it up to 120s
$codespaceName = $null
#$maxAttempts = 30  # previous: ~120s wait
$maxAttempts = 60  # increased attempts (~240s wait)
for ($i = 0; $i -lt $maxAttempts; $i++) {
    Start-Sleep -Seconds 6
    try {
        $listJson = gh codespace list -R samiat-quadir/bar-directory-recon --limit 50 --json name, displayName, state 2>$null | Out-String
        $entries = $null
        if ($listJson) { $entries = ConvertFrom-Json $listJson }
        if ($entries) {
            foreach ($e in $entries) {
                if ($e.displayName -eq $name) {
                    $codespaceName = $e.name
                    if ($e.state -eq 'Available' -or $e.state -eq 'Running') { break }
                }
            }
        }
    }
    catch { }
    if ($codespaceName) { break }
}

if (-not $codespaceName) {
    Write-Output "failed to get codespace: '$name'"
    Write-Output "SUMMARY >> task=ace_health_codespace status=fail branch=$branch codespace=$name tail=''"
    exit 1
}

# Wait a few seconds for container boot
Start-Sleep -Seconds 6

# Additional retry loop: wait for SSH server to be reachable via gh codespace ssh
$sshReady = $false
for ($j = 0; $j -lt 12; $j++) {
    try {
        gh codespace ssh -c $codespaceName -- "echo ready" > $null 2>&1
        $sshReady = $true
        break
    }
    catch {
        Start-Sleep -Seconds 5
    }
}
if (-not $sshReady) {
    Write-Output "error: SSH server not ready in codespace $codespaceName"
    try {
        Write-Output "Attempting codespace rebuild to apply devcontainer features..."
        gh codespace rebuild -c $codespaceName
        # wait for rebuild to complete and SSH to start
        Start-Sleep -Seconds 12
        for ($k = 0; $k -lt 36; $k++) {
            try {
                gh codespace ssh -c $codespaceName -- "echo ready" > $null 2>&1
                $sshReady = $true
                break
            }
            catch {
                Start-Sleep -Seconds 5
            }
        }
        if (-not $sshReady) { Write-Output "Rebuild did not make SSH available in time." }
    }
    catch {
        Write-Output "Rebuild failed or not supported: $($_.Exception.Message)"
    }
}

# 4) Run pytest INSIDE the devcontainer (no network calls, exclude slow/e2e/integration)
try {
    gh codespace ssh -c $codespaceName -- "devcontainer exec --workspace-folder . bash -lc 'pytest -q -k \"not slow and not e2e and not integration\" 2>&1 | tee /tmp/pytest_smoke.txt'"
    $log = gh codespace ssh -c $codespaceName -- "bash -lc 'tail -n +1 /tmp/pytest_smoke.txt'"
}
catch {
    $log = $_.Exception.Message
}

# 5) Stop Codespace
try { gh codespace stop -c $codespaceName } catch { }

# 6) Print summary
$passed = ($log -match 'passed') -and ($log -notmatch 'ERROR') -and ($log -notmatch 'FAILED')
$result = if ($passed) { 'ok' } else { 'fail' }
Write-Output "SUMMARY >> task=ace_health_codespace status=$result branch=$branch codespace=$name tail='$log'"
