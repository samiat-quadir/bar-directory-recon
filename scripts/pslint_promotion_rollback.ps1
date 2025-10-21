# Restore the previous protection snapshot (from preview/decide run)# Restore the previous protection snapshot (from preview/decide run)

Set-StrictMode -Version LatestSet-StrictMode -Version Latest

$ErrorActionPreference='Stop'$ErrorActionPreference='Stop'

$owner=(gh repo view --json owner -q .owner.login)$owner=(gh repo view --json owner -q .owner.login)

$repo=(gh repo view --json name -q .name)$repo=(gh repo view --json name -q .name)

$snap = 'artifacts\pslint\branch_protection_before.json'$snap = 'artifacts\pslint\branch_protection_before.json'

if(!(Test-Path $snap)){ throw 'snapshot not found: artifacts\pslint\branch_protection_before.json' }if(!(Test-Path $snap)){ throw 'snapshot not found: artifacts\pslint\branch_protection_before.json' }

gh api -X PUT "repos/$owner/$repo/branches/main/protection" --input $snapgh api -X PUT "repos/$owner/$repo/branches/main/protection" --input $snap

Write-Host "SUMMARY >> task=pslint_rollback status=ok note=`"branch protection restored from snapshot`""Write-Host "SUMMARY >> task=pslint_rollback status=ok note="branch protection restored from snapshot""
