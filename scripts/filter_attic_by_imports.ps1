# Filter attic_candidates.txt to avoid deleting files that are referenced/imported anywhere in the repo
Set-Location 'C:\Code\bar-directory-recon'
$candidates = Get-Content attic_candidates.txt | Where-Object { $_ -ne '' }
$pyfiles = Get-ChildItem -Path . -Recurse -Include *.py -File | Where-Object { $_.FullName -notmatch '\\\.git\\' }
$final = @()
$kept = @()
foreach($c in $candidates){
  $base = [IO.Path]::GetFileNameWithoutExtension($c)
  $escaped = [regex]::Escape($base)
  $pattern = "\\b$escaped\\b"
  $found = $false
  foreach($p in $pyfiles){
    if(Select-String -Path $p.FullName -Pattern $pattern -Quiet){ $found = $true; break }
  }
  if($found){ $kept += $c } else { $final += $c }
}
$final | Set-Content attic_final_candidates.txt
$kept | Set-Content attic_kept_by_imports.txt
Write-Output "FINAL_COUNT=$($final.Count);KEPT_BY_IMPORTS=$($kept.Count)"
