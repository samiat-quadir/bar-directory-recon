# file: scripts/release_sanity.ps1
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$owner=(gh repo view --json owner -q .owner.login); $repo=(gh repo view --json name -q .name)
$sha = gh api "repos/$owner/$repo/commits/main" --jq .sha
$runs = gh api "repos/$owner/$repo/commits/$sha/check-runs" --paginate | ConvertFrom-Json
$req  = @('audit','fast-tests (ubuntu-latest)','fast-tests (windows-latest)','workflow-guard','ps-lint (ubuntu-latest)','ps-lint (windows-latest)')
$map=@{}; foreach($r in $runs.check_runs){ $map[$r.name]=$r.conclusion }
$bad = $req | Where-Object { $map[$_] -ne 'success' }
$assets = gh release view v0.1.0 --json assets -q '.assets[].name' 2>
$ok = (($bad.Count -eq 0) -and ($assets.Length -gt 0))
Write-Host ("SUMMARY >> task=release_sanity status={0} bad=[{1}] assets={2}" -f ( $ok?'ok':'needs_attention'), ($bad -join ','), (($assets.Length -gt 0)?'present':'missing') )