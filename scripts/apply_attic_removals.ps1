# Apply attic removals listed in attic_to_remove.txt
Set-Location 'C:\Code\bar-directory-recon'
$items = Get-Content attic_to_remove.txt | Where-Object { -not [string]::IsNullOrWhiteSpace($_) }
foreach($p in $items){
  Write-Output "GIT_RM: $p"
  git rm -f -- "$p" 2>&1 | Write-Output
}
# Record git status after attempted removals
git status --porcelain > rm_status.txt
Write-Output "APPLY_REMOVALS_DONE=" + ($items.Count)
