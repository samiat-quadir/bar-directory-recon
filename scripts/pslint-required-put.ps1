param([switch]$Execute,[string]$Branch='main')
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
function Req($context){ @{ context = $context } }
$owner=(gh repo view --json owner -q .owner.login)
$repo=(gh repo view --json name -q .name)
# Build JSON with ps-lint contexts ADDED for scripts/** (dry-run by default)
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
  enforce_admins = @{ enabled = $true }
}
$json = $payload | ConvertTo-Json -Depth 6
[IO.File]::WriteAllText('artifacts\branch_protection_pslint.json',$json,[Text.UTF8Encoding]::new($false))
Write-Host "WROTE: artifacts\branch_protection_pslint.json (preview)."
Write-Host "To apply, run: .\scripts\pslint-required-put.ps1 -Execute"
if ($Execute) {
  $cmd = "gh api -X PUT -H 'Accept: application/vnd.github+json' repos/$owner/$repo/branches/$Branch/protection -f required_status_checks:=@artifacts/branch_protection_pslint.json"
  Write-Host "RUNNING: $cmd"
  Invoke-Expression $cmd
  Write-Host "APPLIED branch protection to $Branch"
} else {
  Write-Host 'Dry-run: API call not executed.'
}

