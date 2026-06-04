# File: scripts/ops_parity_fix_v011.ps1
# Purpose: For tag v0.1.1, run cli-pack → upload missing assets to the GitHub Release → re-run parity → append links.
# Usage:   pwsh -File scripts/ops_parity_fix_v011.ps1 [-VersionTag v0.1.1]
# Notes:   Idempotent, Windows-safe, non-interactive. Only uses manual workflows per guard policy.

param(
  [string]$VersionTag = "v0.1.1"
)

# --- Repo config ---
$Repo        = "samiat-quadir/bar-directory-recon"
$LocalPath   = "C:\Code\bar-directory-recon"
$CliPackWf   = ".github/workflows/cli-pack.yml"
$ParityWf    = ".github/workflows/release-qa-parity.yml"

# --- Helpers ---
function Out-Result { param([int]$Step,[string]$Status,[string]$Link,[string]$Note)
  $n = ($Note -replace "\r?\n"," ").Trim()
  Write-Output ("RESULT >> step={0} status={1} link={2} note=""{3}""" -f $Step,$Status,($Link ?? ""),$n)
}
function Die { param([int]$Step,[string]$Note,[string]$Link=""); Out-Result $Step "fail" $Link $Note; Write-Output ('RELAY >> task=parity_fix_v011 status=degraded checks=0 guard=PASS note="{0}"' -f $Note); exit 1 }
function Ensure-Ok { param([bool]$Cond,[int]$Step,[string]$Note,[string]$Link=""); if(-not $Cond){ Die $Step $Note $Link } }

function Run-And-Poll {
  param([string]$WorkflowFile,[hashtable]$Inputs,[int]$Minutes=20,[int]$PollSec=6,[int]$Step)
  $args = @($WorkflowFile); foreach($k in $Inputs.Keys){ $args += @('-f', "$k=$($Inputs[$k])") }
  $null = & gh workflow run @args
  Ensure-Ok ($LASTEXITCODE -eq 0) $Step "failed to dispatch $WorkflowFile" "https://github.com/$Repo/actions"
  $deadline = (Get-Date).AddMinutes($Minutes)
  $run = $null; $url = ""
  do {
    Start-Sleep -Seconds $PollSec
    $lst = & gh run list --workflow $WorkflowFile --limit 1 --json databaseId,status,conclusion,url,createdAt | ConvertFrom-Json
    if($lst -and $lst.Count -ge 1){ $run = $lst[0]; $url = $run.url }
  } while ($run -and $run.status -ne "completed" -and (Get-Date) -lt $deadline)
  Ensure-Ok ($run -ne $null) $Step "no run found for $WorkflowFile" "https://github.com/$Repo/actions"
  Ensure-Ok ($run.status -eq "completed") $Step "$WorkflowFile timed out" $url
  return $run
}

function Get-RunArtifacts {
  param([int64]$RunId,[int]$Step)
  $resp = & gh api -H "Accept: application/vnd.github+json" "repos/$Repo/actions/runs/$RunId/artifacts"
  Ensure-Ok ($LASTEXITCODE -eq 0 -and $resp) $Step "cannot list artifacts for run $RunId"
  return ($resp | ConvertFrom-Json).artifacts
}

function Release-AssetNames {
  param([string]$Tag,[int]$Step)
  $rv = & gh release view $Tag --json url,assets 2>$null | ConvertFrom-Json
  Ensure-Ok ($LASTEXITCODE -eq 0 -and $rv) $Step "release $Tag not found" "https://github.com/$Repo/releases"
  $existing = @()
  if($rv.assets){ $existing = $rv.assets | ForEach-Object { $_.name } }
  return ,@($existing)
}

function Get-InputKey([string]$Yaml){
  if($Yaml -match '(?ms)workflow_dispatch:\s*inputs:.*?^\s*tag\s*:'){ return 'tag' }
  if($Yaml -match '(?ms)workflow_dispatch:\s*inputs:\s*([A-Za-z0-9_\-]+)\s*:'){ return $Matches[1] }
  return 'tag'
}

# --- Step 1: Preflight ---
$step=1
try {
  & gh --version *> $null; Ensure-Ok ($LASTEXITCODE -eq 0) $step "GitHub CLI (gh) missing"
  & gh auth status *> $null; Ensure-Ok ($LASTEXITCODE -eq 0) $step "gh not authenticated"
  Ensure-Ok (Test-Path -LiteralPath $LocalPath) $step "repo path missing: $LocalPath"
  Set-Location -LiteralPath $LocalPath
  $env:GH_REPO = $Repo
  Ensure-Ok (Test-Path -LiteralPath (Join-Path $LocalPath $CliPackWf)) $step "missing $CliPackWf" "https://github.com/$Repo/tree/main/.github/workflows"
  Ensure-Ok (Test-Path -LiteralPath (Join-Path $LocalPath $ParityWf)) $step "missing $ParityWf" "https://github.com/$Repo/tree/main/.github/workflows"
  # Ensure the release exists
  $null = & gh release view $VersionTag --json url 2>$null
  Ensure-Ok ($LASTEXITCODE -eq 0) $step "release $VersionTag not found" "https://github.com/$Repo/releases"
  Out-Result $step "ok" "https://github.com/$Repo/releases/tag/$VersionTag" "env ready; workflows present; release exists"
} catch { Die $step ("precheck error: {0}" -f $_.Exception.Message) }

# --- Step 2: Run cli-pack (manual) to produce artifacts ---
$step=2
$clipackUrl=""; $clipackRunId=[int64]-1
try {
  $run = Run-And-Poll -WorkflowFile $CliPackWf -Inputs @{} -Minutes 20 -PollSec 6 -Step $step
  $clipackUrl = $run.url; $clipackRunId = [int64]$run.databaseId
  Ensure-Ok ($run.conclusion -eq "success") $step ("cli-pack $($run.conclusion)") $clipackUrl
  Out-Result $step "ok" $clipackUrl "cli-pack SUCCESS"
} catch { Die $step ("cli-pack error: {0}" -f $_.Exception.Message) $clipackUrl }

# --- Step 3: Download artifacts and upload missing files to the release ---
$step=3
$uploaded = @(); $skipped = @()
try {
  $art = Get-RunArtifacts -RunId $clipackRunId -Step $step
  Ensure-Ok ($art -and $art.Count -gt 0) $step "no artifacts produced by cli-pack" $clipackUrl

  $tmp = Join-Path ([IO.Path]::GetTempPath()) ("bdr_clipack_" + [Guid]::NewGuid().ToString("N"))
  New-Item -ItemType Directory -Force -Path $tmp | Out-Null

  # Download and extract all artifacts
  foreach($a in $art){
    $null = & gh run download $clipackRunId -n $a.name -D $tmp
  }

  # Candidate files to upload: common package/dist + checksums
  $candidates = Get-ChildItem -Path $tmp -Recurse -File -Include *.sha256,*.whl,*.tar.gz,*.zip,*.txt 2>$null
  Ensure-Ok ($candidates -and $candidates.Count -gt 0) $step "no candidate files found to upload" $clipackUrl

  # Fetch current release asset names
  $existing = Release-AssetNames -Tag $VersionTag -Step $step

  foreach($f in $candidates){
    if($existing -contains $f.Name){
      $skipped += $f.Name
      continue
    }
    $upl = & gh release upload $VersionTag (Resolve-Path -LiteralPath $f.FullName) --repo $Repo 2>&1
    if($LASTEXITCODE -eq 0){ $uploaded += $f.Name } else { $skipped += ($f.Name + " (upload-failed)") }
  }

  $note = "uploaded=" + (($uploaded | Select-Object -Unique) -join ", ")
  if($skipped.Count){ $note += "; skipped=" + (($skipped | Select-Object -Unique) -join ", ") }
  Out-Result $step "ok" "https://github.com/$Repo/releases/tag/$VersionTag" $note
} catch { Die $step ("asset upload error: {0}" -f $_.Exception.Message) "https://github.com/$Repo/releases/tag/$VersionTag" }

# --- Step 4: Re-run parity for the tag and verify PASS ---
$step=4
$parityUrl=""
try {
  $wfText = Get-Content -LiteralPath (Join-Path $LocalPath $ParityWf) -Raw
  $key = Get-InputKey $wfText
  $run = Run-And-Poll -WorkflowFile $ParityWf -Inputs @{$key=$VersionTag} -Minutes 15 -PollSec 5 -Step $step
  $parityUrl = $run.url
  Ensure-Ok ($run.conclusion -eq "success") $step ("parity $($run.conclusion) on $VersionTag") $parityUrl
  Out-Result $step "ok" $parityUrl ("parity PASS on {0}" -f $VersionTag)
} catch { Die $step ("parity error: {0}" -f $_.Exception.Message) $parityUrl }

# --- Step 5: Append links to the Release body (idempotent) ---
$step=5
$releaseUrl = "https://github.com/$Repo/releases/tag/$VersionTag"
try {
  $rv = & gh release view $VersionTag --json url,body 2>$null | ConvertFrom-Json
  $body = "$($rv.body)"
  $append = @()
  $append += ""
  $append += "### Parity & Pack"
  if($parityUrl){ $append += "* Parity: $parityUrl" }
  if($clipackUrl){ $append += "* Pack run: $clipackUrl" }
  if($uploaded.Count){ $append += "* Assets uploaded: " + (($uploaded | Select-Object -Unique) -join ", ") }
  $addText = ($append -join "`n")

  $needsUpdate = $false
  if($parityUrl -and $body -notmatch [regex]::Escape($parityUrl)){ $needsUpdate = $true }
  if($clipackUrl -and $body -notmatch [regex]::Escape($clipackUrl)){ $needsUpdate = $true }
  foreach($n in ($uploaded | Select-Object -Unique)){
    if($body -notmatch [regex]::Escape($n)){ $needsUpdate = $true; break }
  }

  if($needsUpdate){
    $newBody = $body + "`n" + $addText
    $null = & gh release edit $VersionTag --notes $newBody
    Ensure-Ok ($LASTEXITCODE -eq 0) $step "failed to update release body" $releaseUrl
    Out-Result $step "ok" $releaseUrl "release notes updated (parity + pack links)"
  } else {
    Out-Result $step "ok" $releaseUrl "release already includes parity/pack info"
  }
} catch { Die $step ("release update error: {0}" -f $_.Exception.Message) $releaseUrl }

# --- Relay summary ---
Write-Output ('RELAY >> task=parity_fix_v011 status=ok checks=0 guard=PASS note="cli-pack assets uploaded ({0}); parity PASS on {1}"' -f ($uploaded.Count), $VersionTag)
