param([string]$csName)
if (-not $csName) { Write-Error 'Missing codespace name'; exit 2 }

$remoteCmd = 'bash -lc ''pytest -q -k "not slow and not e2e and not integration" 2>&1 | tail -n 1'''

Write-Output "Executing remote test on $csName..."

$args = @('codespace','ssh','-c',$csName,'--',$remoteCmd)
$proc = Start-Process -FilePath 'gh' -ArgumentList $args -NoNewWindow -Wait -PassThru -RedirectStandardOutput 'ssh_stdout.txt' -RedirectStandardError 'ssh_stderr.txt'

$out = Get-Content -Raw -ErrorAction SilentlyContinue 'ssh_stdout.txt'
$err = Get-Content -Raw -ErrorAction SilentlyContinue 'ssh_stderr.txt'
Remove-Item -ErrorAction SilentlyContinue 'ssh_stdout.txt','ssh_stderr.txt'

if ($proc.ExitCode -ne 0) {
    Write-Output "REMOTE_FAILED: $err"
    $lastLine = ($err -split "`n" | Where-Object { $_ -ne '' } | Select-Object -Last 1) -join ''
} else {
    $lastLine = ($out -split "`n" | Where-Object { $_ -ne '' } | Select-Object -Last 1) -join ''
}

Write-Output "Remote last line: $lastLine"

Write-Output "Stopping Codespace $csName..."
& gh codespace stop -c $csName | Out-Null

if ($LASTEXITCODE -ne 0) {
    $status = 'degraded'
} else {
    $status = 'ok'
}

Write-Output "SUMMARY >> task=ace_codespace_smoke status=$status cs=$csName tail='$lastLine' note='auto-create-run'"
