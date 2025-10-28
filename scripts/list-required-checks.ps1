param([string]$Branch = "main")
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$owner = (gh repo view --json owner -q .owner.login); $repo = (gh repo view --json name -q .name)
$prot = gh api -H "Accept: application/vnd.github+json" "repos/$owner/$repo/branches/$Branch/protection" | ConvertFrom-Json
$req = @()
if($prot.required_status_checks -and $prot.required_status_checks.checks){ $req = $prot.required_status_checks.checks | % { $_.context } }
Write-Host ("required checks on {0}: {1}" -f $Branch, ($req -join ", "))