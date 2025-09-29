# Compute attic candidates for cleanup
Set-Location 'C:\Code\bar-directory-recon'
$patterns = @(
  'archive/',
  'automation/',
  '^async_.*\\.py$',
  '^complete_verification\\.py$',
  '^run_cross_device_task\\.py$',
  '^tools/auto_conflict_resolver\\.py$',
  '^scripts/auto_.*\\.py$',
  'temp_reusable\\.yml$'
)
$namepat = '(?i)(?:^|[\\/])(ali|ace|asus|alienware|mothership|work[-_ ]?desktop)(?:[\\/]|$)'
$all = git ls-files | Sort-Object
$keep = @()
$drop = @()
foreach($f in $all){
  if($f -like '.github/*' -or $f -like '.devcontainer/*' -or $f -like 'tests/*' -or $f -eq 'pyproject.toml'){ $keep += $f; continue }
  if($f -match $namepat){ $drop += $f; continue }
  $hit = $false
  foreach($p in $patterns){ if($f -match $p){ $hit = $true; break } }
  if($hit){ $drop += $f } else { $keep += $f }
}
$drop | Set-Content attic_candidates.txt
$keep | Set-Content attic_keep.txt

# Filter .py files that are referenced by tests or src; avoid deleting files used by tests
$searchPaths = @()
if(Test-Path 'tests'){ $searchPaths += (Get-ChildItem -Path 'tests' -Recurse -File -ErrorAction SilentlyContinue | Select-Object -ExpandProperty FullName) }
if(Test-Path 'src'){ $searchPaths += (Get-ChildItem -Path 'src' -Recurse -File -ErrorAction SilentlyContinue | Select-Object -ExpandProperty FullName) }
$removes = @()
$keepsFiltered = @()
foreach($f in $drop){
  if([string]::IsNullOrWhiteSpace($f)){ continue }
  if($f -match '\.py$' -and $searchPaths.Count -gt 0){
    $name = [io.path]::GetFileNameWithoutExtension($f)
    $found = Select-String -Path $searchPaths -Pattern ([regex]::Escape($name)) -Quiet -ErrorAction SilentlyContinue
    if($found){
      $keepsFiltered += $f
    } else {
      $removes += $f
    }
  } else {
    $removes += $f
  }
}
$removes | Set-Content attic_to_remove.txt
$keepsFiltered | Set-Content attic_keep_filtered.txt
Write-Output "REMOVE_COUNT=$($removes.Count); KEEP_FILTERED_COUNT=$($keepsFiltered.Count)"
