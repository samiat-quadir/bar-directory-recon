# file: scripts/release_parity_local.ps1
param(
  [Parameter(Mandatory=$true)][string]$Tag
)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
function Say($m){ Write-Host "==> $m" }
function Sha256($p){ (Get-FileHash -Algorithm SHA256 -Path $p).Hash.ToLower() }

git fetch origin --prune *> $null
git checkout -q main
git reset --hard origin/main
git clean -xdf -q

$root = Join-Path $PWD "artifacts\release\$Tag-local"
if(Test-Path $root){ Remove-Item -Recurse -Force $root }
New-Item -ItemType Directory -Path $root | Out-Null

# Export + build
git archive -o (Join-Path $root "$Tag-src.zip") $Tag
Expand-Archive -Path (Join-Path $root "$Tag-src.zip") -DestinationPath (Join-Path $root "src")
Push-Location (Join-Path $root "src")
python -m pip install -U pip build > $null
python -m build > $null
Pop-Location

# Download release assets
$rel = Join-Path $root "release-assets"
New-Item -ItemType Directory -Path $rel | Out-Null
gh release download $Tag --pattern "*.whl" --pattern "*.tar.gz" --dir $rel --clobber | Out-Null

# Compare
$rebuilt = Get-ChildItem (Join-Path $root "src\dist") -Include *.whl,*.tar.gz -File
$release = Get-ChildItem $rel -Include *.whl,*.tar.gz -File

$pairs = @()
foreach($r in $release){
  $name = $r.Name
  $loc = $rebuilt | Where-Object { $_.Name -eq $name } | Select-Object -First 1
  $shaRel = Sha256 $r.FullName
  $shaLoc = if($loc){ Sha256 $loc.FullName } else { $null }
  $pairs += [pscustomobject]@{ name=$name; sha_rebuild=$shaLoc; sha_release=$shaRel; match=($null -ne $shaLoc -and $shaLoc -eq $shaRel) }
}
$badPairs = @($pairs | Where-Object { -not $_.match })
$mis = @($badPairs).Count
if($mis -eq 0){ $statusText = "ok" } else { $statusText = "attention" }
Write-Host ("SUMMARY >> task=local_parity tag=$Tag status={0} mismatches=$mis" -f $statusText)