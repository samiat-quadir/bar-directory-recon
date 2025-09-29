# Remove common artifact files that break linters/mypy
Set-Location 'C:\Code\bar-directory-recon'
$items = Get-ChildItem -Recurse -Include '*.new','*.orig','*.rej','*.corrupted' -File -ErrorAction SilentlyContinue
if(-not $items){ Write-Output 'NO_ARTIFACTS_FOUND'; exit 0 }
foreach($it in $items){
  Write-Output "RM: $($it.FullName)"
  git rm -f -- "$($it.FullName)" 2>&1 | Write-Output
}
# write status
git status --porcelain > rm_status.txt
Write-Output 'REMOVALS_DONE'