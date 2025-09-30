$ErrorActionPreference = 'Stop'

# 0) Scopes check
$authStatus = gh auth status 2>&1
if (-not ($authStatus | Select-String -Pattern 'codespace')) {
    Write-Host "ACTION_NEEDED: gh auth refresh -h github.com -s codespace -s repo -s workflow"
    Write-Host "SUMMARY >> task=ace_smoke_main status=blocked reason=missing_scope"
    exit 0
}

# 1) Create codespace (capture output)
$dn = "bdr-ace-verify-" + (Get-Date -Format yyyyMMdd-HHmm) + "-" + (Get-Random)
Write-Host "Creating Codespace: $dn"
$oldEAP = $ErrorActionPreference
$ErrorActionPreference = 'Continue'
$createOut = gh codespace create -R samiat-quadir/bar-directory-recon -b main -m standardLinux32gb --idle-timeout 45m --retention-period 24h --display-name $dn --default-permissions 2>&1
$createExit = $LASTEXITCODE
$ErrorActionPreference = $oldEAP
Write-Host "CREATE_EXIT=$createExit"
Write-Host "CREATE_OUT_START"
Write-Host $createOut
Write-Host "CREATE_OUT_END"

# 2) Resolve name
$name = $null
for ($i = 0; $i -lt 20; $i++) {
    Start-Sleep -s 6
    $x = gh codespace list --json name, displayName, state, repository | ConvertFrom-Json
    $e = $x | Where-Object { $_.displayName -eq $dn -and $_.repository -like '*bar-directory-recon*' }
    if ($e) { $name = $e.name; break }
}
if (-not $name) { Write-Host "SUMMARY >> task=ace_smoke_main status=fail reason=no_name_after_create"; exit 1 }
Write-Host "Resolved Codespace name: $name"

# 3) Wait for Available
for ($i = 0; $i -lt 30; $i++) {
    Start-Sleep -s 6
    $sobj = (gh codespace list --json name, state | ConvertFrom-Json | Where-Object { $_.name -eq $name })
    $s = if ($sobj) {
        if ($sobj.state -is [System.Array]) { ($sobj.state -join ',') } else { $sobj.state }
    }
    else { 'Missing' }
    Write-Host ("poll {0} state={1}" -f $i, $s)
    if ($s -like '*Available*') { break }
}
$sobj = (gh codespace list --json name, state | ConvertFrom-Json | Where-Object { $_.name -eq $name })
$sfinal = if ($sobj) { if ($sobj.state -is [System.Array]) { ($sobj.state -join ',') } else { $sobj.state } } else { 'Missing' }
if (-not $sobj -or $sfinal -notlike '*Available*') { gh codespace stop -c $name *> $null; Write-Host "SUMMARY >> task=ace_smoke_main status=fail reason=never_available"; exit 1 }
Write-Host "Codespace is Available"

# 4) Prepare remote smoke script (bash) and run it via piping
$bash = @'
#!/usr/bin/env bash
set -e
cd /workspaces/*bar-directory-recon* 2>/dev/null || cd /workspaces/bar-directory-recon 2>/dev/null || cd "$HOME"
bash .devcontainer/setup.sh || true
pip install -r requirements-dev.txt -q || true
pip install -e .[dev] -q || true
set +e
pytest -p no:cacheprovider -o addopts="" -q --maxfail=1 universal_recon/tests tests -k "not slow and not e2e and not integration" > /tmp/pytest_smoke.txt 2>&1
code=$?
set -e
tail -n 20 /tmp/pytest_smoke.txt || true
echo "RUN_EXIT=$code"
'@

# remove any CR characters to avoid $'...\r' issues when piping to a remote shell
$bash = $bash -replace "`r", ""

Write-Host "Uploading and executing /tmp/smoke.sh on codespace $name"
# encode as base64 locally to avoid CRLF/quoting issues, decode remotely and execute
Write-Host "Piping bash script into codespace and executing via 'bash -s'"
$out = $bash | gh codespace ssh -c $name -- 'bash -s'

# 5) Stop only that Codespace
Write-Host "Stopping codespace: $name"
gh codespace stop -c $name *> $null

# 6) Parse output and print summary
$lines = $out -split "`r?`n"
$exitLine = $lines | Where-Object { $_ -match '^RUN_EXIT=' } | Select-Object -Last 1
$exit = if ($exitLine) { ($exitLine -replace 'RUN_EXIT=', '') } else { '1' }
if (-not [int]::TryParse($exit, [ref]$null)) { $exit = '1' }
if (([int]$exit -eq 0) -and ($out -match ' passed,')) { $status = 'ok' } else { $status = 'degraded' }
$tail = if ($lines.Count -gt 0) { $lines[-1] } else { '' }
Write-Host "SUMMARY >> task=ace_smoke_main status=$status exit=$exit cs=$name tail='$tail'"

# done
exit ([int]$exit)
$createExit = $LASTEXITCODE
$ErrorActionPreference = $oldEAP
Write-Host "CREATE_EXIT=$createExit"
Write-Host "CREATE_OUT_START"
Write-Host $createOut
Write-Host "CREATE_OUT_END"

# 2) Resolve name
$name = $null
for ($i = 0; $i -lt 20; $i++) {
    Start-Sleep -s 6
    $x = gh codespace list --json name, displayName, state, repository | ConvertFrom-Json
    $e = $x | Where-Object { $_.displayName -eq $dn -and $_.repository -like '*bar-directory-recon*' }
    if ($e) { $name = $e.name; break }
}
if (-not $name) { Write-Host "SUMMARY >> task=ace_smoke_main status=fail reason=no_name_after_create"; exit 1 }
Write-Host "Resolved Codespace name: $name"

# 3) Wait for Available
for ($i = 0; $i -lt 30; $i++) {
    Start-Sleep -s 6
    $sobj = (gh codespace list --json name, state | ConvertFrom-Json | Where-Object { $_.name -eq $name })
    $s = if ($sobj) {
        if ($sobj.state -is [System.Array]) { ($sobj.state -join ',') } else { $sobj.state }
    }
    else { 'Missing' }
    Write-Host ("poll {0} state={1}" -f $i, $s)
    if ($s -like '*Available*') { break }
}
$sobj = (gh codespace list --json name, state | ConvertFrom-Json | Where-Object { $_.name -eq $name })
$sfinal = if ($sobj) { if ($sobj.state -is [System.Array]) { ($sobj.state -join ',') } else { $sobj.state } } else { 'Missing' }
if (-not $sobj -or $sfinal -notlike '*Available*') { gh codespace stop -c $name *> $null; Write-Host "SUMMARY >> task=ace_smoke_main status=fail reason=never_available"; exit 1 }
Write-Host "Codespace is Available"

# 4) Prepare remote smoke script (bash) and run it via piping
$bash = @'
#!/usr/bin/env bash
set -e
cd /workspaces/*bar-directory-recon* 2>/dev/null || cd /workspaces/bar-directory-recon 2>/dev/null || cd "$HOME"
bash .devcontainer/setup.sh || true
pip install -r requirements-dev.txt -q || true
pip install -e .[dev] -q || true
set +e
pytest -p no:cacheprovider -o addopts="" -q --maxfail=1 universal_recon/tests tests -k "not slow and not e2e and not integration" > /tmp/pytest_smoke.txt 2>&1
code=$?
set -e
tail -n 20 /tmp/pytest_smoke.txt || true
echo "RUN_EXIT=$code"
'@

# remove any CR characters to avoid $'...\r' issues when piping to a remote shell
$bash = $bash -replace "`r", ""

Write-Host "Uploading and executing /tmp/smoke.sh on codespace $name"
# encode as base64 locally to avoid CRLF/quoting issues, decode remotely and execute
Write-Host "Piping bash script into codespace and executing via 'bash -s'"
$out = $bash | gh codespace ssh -c $name -- 'bash -s'

# 5) Stop only that Codespace
Write-Host "Stopping codespace: $name"
gh codespace stop -c $name *> $null

# 6) Parse output and print summary
$lines = $out -split "`r?`n"
$exitLine = $lines | Where-Object { $_ -match '^RUN_EXIT=' } | Select-Object -Last 1
$exit = if ($exitLine) { ($exitLine -replace 'RUN_EXIT=', '') } else { '1' }
if (-not [int]::TryParse($exit, [ref]$null)) { $exit = '1' }
if (([int]$exit -eq 0) -and ($out -match ' passed,')) { $status = 'ok' } else { $status = 'degraded' }
$tail = if ($lines.Count -gt 0) { $lines[-1] } else { '' }
Write-Host "SUMMARY >> task=ace_smoke_main status=$status exit=$exit cs=$name tail='$tail'"

# done
exit ([int]$exit)
