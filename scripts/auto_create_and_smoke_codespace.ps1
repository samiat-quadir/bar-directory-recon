param(
    [string]$Repo = 'samiat-quadir/bar-directory-recon',
    [string]$Branch = 'main'
)

function Write-ActionNeededAndExit($msg) {
    Write-Output "ACTION_NEEDED: $msg"
    exit 2
}

try {
    $auth = gh auth status --hostname github.com 2>&1
}
catch {
    Write-ActionNeededAndExit 'gh auth status failed; ensure gh is installed and authenticated.'
}

# Normalize output (handle arrays) and perform case-insensitive search for codespace scope
$authText = if ($auth -is [System.Array]) { $auth -join "`n" } else { [string]$auth }
if (-not ($authText -match '(?i)codespace')) {
    Write-ActionNeededAndExit 'gh auth refresh -h github.com -s codespace -s repo -s workflow'
}

$display = "bdr-ace-smoke-$(Get-Date -Format yyyyMMdd-HHmm)-$((Get-Random) % 10000)"

Write-Output "Creating Codespace with display-name='$display'..."

$createCmd = @(
    'gh', 'codespace', 'create',
    '-R', $Repo,
    '-b', $Branch,
    '-m', 'standardLinux32gb',
    '--idle-timeout', '45m',
    '--retention-period', '72h',
    '--display-name', $display,
    '--default-permissions'
)

$createProc = Start-Process -FilePath 'gh' -ArgumentList $createCmd[1..($createCmd.Length - 1)] -NoNewWindow -Wait -PassThru -RedirectStandardOutput 'stdout.txt' -RedirectStandardError 'stderr.txt'
$stdout = Get-Content -Raw -ErrorAction SilentlyContinue 'stdout.txt'
$stderr = Get-Content -Raw -ErrorAction SilentlyContinue 'stderr.txt'
Remove-Item -ErrorAction SilentlyContinue 'stdout.txt', 'stderr.txt'

if ($createProc.ExitCode -ne 0) {
    Write-Output "CREATE_FAILED: $stderr";
    exit 3
}

Write-Output "Created. Polling for Available state..."

function Get-CodespaceByDisplay($display) {
    $listRaw = gh codespace list --json name, displayName, repository, state, lastUsedAt 2>$null
    if (-not $listRaw) { return $null }
    $list = $listRaw | ConvertFrom-Json
    return $list | Where-Object { $_.displayName -eq $display }
}

$timeout = [DateTime]::UtcNow.AddMinutes(12)
$selected = $null
while ([DateTime]::UtcNow -lt $timeout) {
    Start-Sleep -Seconds 6
    try {
        $sel = Get-CodespaceByDisplay $display
    }
    catch {
        $sel = $null
    }
    if ($sel -and $sel.state -eq 'Available') { $selected = $sel; break }
}

if (-not $selected) {
    Write-Output "NO_AVAILABLE: created codespace did not reach Available within timeout"
    exit 4
}

$csName = $selected.name
Write-Output "Selected codespace: $csName (display: $display)"

Write-Output "Running smoke pytest tail..."

# Build remote command carefully to avoid PowerShell parsing issues
$remote = 'bash -lc "pytest -q -k \"not slow and not e2e and not integration\" 2>&1 | tail -n 1"'
$sshCmd = "gh codespace ssh -c $csName -- $remote"

try {
    $sshOut = Invoke-Expression $sshCmd 2>&1
}
catch {
    $sshOut = $_.Exception.Message
}

$lastLine = ($sshOut | Where-Object { $_ -ne '' } | Select-Object -Last 1) -join ''

Write-Output "Test tail: $lastLine"

Write-Output "Stopping Codespace $csName..."
& gh codespace stop -c $csName | Out-Null

if ($LASTEXITCODE -ne 0) {
    Write-Output "STOP_FAILED for $csName"
    $status = 'degraded'
}
else {
    $status = 'ok'
}

Write-Output "SUMMARY >> task=ace_codespace_smoke status=$status cs=$csName tail='$lastLine' note='auto-create-run'"
