# Auto-resolve files containing Git merge markers
Set-Location 'C:\Code\bar-directory-recon'
$conflicted = Get-ChildItem -Recurse -File -ErrorAction SilentlyContinue | Where-Object { Select-String -Path $_.FullName -Pattern '^(<<<<<<< |>>>>>>> |=======$)' -Quiet }
Write-Output ("CONFLICT_FILES_FOUND=" + $conflicted.Count)
$attic = @()
if(Test-Path 'attic_to_remove.txt'){ $attic = Get-Content attic_to_remove.txt | Where-Object { $_ -ne '' } }
foreach($f in $conflicted){
  $rel = $f.FullName.Substring((Get-Location).Path.Length+1).Replace('\\','/')
  if($attic -contains $rel){
    Write-Output ("Attic file conflicted -> removing: $rel")
    git rm -f -- $rel 2>&1 | Write-Output
    continue
  }
  # Prefer origin/main version when available
  try{
    $theirs = git show origin/main:$rel 2>$null
    if($null -ne $theirs -and $theirs -ne ''){
      Write-Output ("Replacing {0} with origin/main version" -f $rel)
      Set-Content -Path $rel -Value $theirs -Encoding UTF8
      git add $rel
      continue
    }
  } catch { Write-Output ("origin/main version not available for {0}: {1}" -f $rel, $_) }

  # Fallback: remove conflict markers from current file, keep local content
  Write-Output ("Cleaning conflict markers from $rel (keeping local content)")
  $txt = Get-Content $rel -Raw
  $clean = $txt -replace '(?s)^<<<<<<<.*?^=======$','' -replace '(?s)^>>>>>>>.*?$',''
  # Also remove any leftover divider lines
  $clean = $clean -replace '^=======$',''
  Set-Content -Path $rel -Value $clean -Encoding UTF8
  git add $rel
}
# Record status
git status --porcelain > auto_resolve_status.txt
Write-Output "AUTO_RESOLVE_DONE"
