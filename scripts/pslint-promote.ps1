param([switch]$Execute,[string]$Branch='main')
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
function Req($context){ @{ context = $context } }
$owner=(gh repo view --json owner -q .owner.login)
$repo=(gh repo view --json name -q .name)
# Build JSON with ps-lint contexts ADDED for scripts/** (future use)
$payload = @{
  required_status_checks = @{
    strict = $true
    checks = @(
      Req('audit'),
      Req('fast-tests (ubuntu-latest)'),
      Req('fast-tests (windows-latest)'),
      Req('workflow-guard'),
      Req('ps-lint (ubuntu-latest)'),
      Req('ps-lint (windows-latest)')
    )
  }
} | ConvertTo-Json -Depth 6
[IO.File]::WriteAllText('artifacts\branch_protection_pslint.json',$payload,[Text.UTF8Encoding]::new($false))
$cmd = "gh api -X PUT -H `"Accept: application/vnd.github+json`" repos/$owner/$repo/branches/$Branch/protection -f required_status_checks:=@artifacts/branch_protection_pslint.json"
Write-Host "PREVIEW >> $cmd"
if($Execute){ iex $cmd; Write-Host "APPLIED." } else { Write-Host "Dry-run only (no changes)." }