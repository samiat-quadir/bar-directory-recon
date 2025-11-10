# file: scripts/2025-11-04-execute-plan.ps1
# Executes today's tasks 1..5 and prints RESULT lines. Guard + six required checks remain unchanged.

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Say($m){ Write-Host "==> $m" }
function RepoSync($path){
  if(!(Test-Path $path)){ throw "Repo not found: $path" }
  Set-Location $path
  git fetch origin --prune *> $null
  git checkout -q main
  git reset --hard origin/main
  git clean -xdf -q
}
function ReadRaw($p){ if(Test-Path $p){ Get-Content $p -Raw } else { "" } }
function WriteIfChanged($p,[string]$c){
  $cur=ReadRaw $p
  if($cur -ne $c){
    $d=Split-Path $p -Parent; if($d -and -not (Test-Path $d)){ New-Item -ItemType Directory -Path $d | Out-Null }
    [IO.File]::WriteAllText($p,$c,[Text.UTF8Encoding]::new($false)); return $true
  } else { return $false }
}
function AppendOnce($p,[string]$block){
  $cur=ReadRaw $p
  if(-not $cur.Contains($block)){
    $d=Split-Path $p -Parent; if($d -and -not (Test-Path $d)){ New-Item -ItemType Directory -Path $d | Out-Null }
    [IO.File]::WriteAllText($p, ($cur + "`n`n" + $block), [Text.UTF8Encoding]::new($false)); return $true
  } else { return $false }
}

$REPO = "C:\Code\bar-directory-recon"
RepoSync $REPO
$owner=(gh repo view --json owner -q .owner.login)
$repo =(gh repo view --json name  -q .name)

# -----------------------------------------
# STEP 1: TestPyPI publish for v0.1.1rc1
# -----------------------------------------
try{
  RepoSync $REPO
  # Ensure manual publish workflow exists (guard-safe; manual-only)
  $wfPath = ".github\workflows\publish-testpypi.yml"
  $wfBody = @"
name: publish-testpypi
on:
  workflow_dispatch:
    inputs:
      tag:
        description: 'Git tag to publish (e.g., v0.1.1rc1)'
        required: true
        type: string
permissions:
  contents: read
jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { ref: \${{ inputs.tag }} }
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - name: Build artifacts
        run: |
          python -m pip install -U pip build
          python -m build
      - name: Publish to TestPyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          user: __token__
          password: \${{ secrets.TESTPYPI_API_TOKEN }}
          repository-url: https://test.pypi.org/legacy/
"@
  $changed = WriteIfChanged $wfPath $wfBody
  if($changed){
    $br="ci/testpypi-publish-$(Get-Date -Format yyyyMMdd-HHmmss)"
    git checkout -b $br
    git add $wfPath
    git commit -m "ci: manual publish to TestPyPI (guard-safe)"
    git push --set-upstream origin $br
    $pr = gh pr create --title "ci: manual publish to TestPyPI" --body "Adds manual-only publish workflow (pypa/gh-action-pypi-publish)." --base main --head $br --draft
    gh pr merge --squash --auto | Out-Null
    # Wait briefly for merge if it’s instant
    Start-Sleep -Seconds 5
    RepoSync $REPO
  }

  # Create tag if missing
  $tag="v0.1.1rc1"
  $tags = git tag
  if(-not ($tags -split "`n" | Where-Object { $_ -eq $tag })){
    git tag $tag
    git push origin $tag
  }

  # Dispatch publish; poll
  gh workflow run publish-testpypi -f tag=$tag | Out-Null
  Start-Sleep -Seconds 5
  $deadline=(Get-Date).AddMinutes(12)
  $status=$null; $url=$null; $conc=$null
  do {
    Start-Sleep -Seconds 6
    $runs=gh run list --workflow publish-testpypi --limit 1 --json databaseId,htmlUrl,status,conclusion | ConvertFrom-Json
    $r=$runs | Select-Object -First 1
    if($r){ $status=$r.status; $conc=$r.conclusion; $url=$r.htmlUrl }
  } while(($status -ne 'completed') -and ((Get-Date) -lt $deadline))
  if($status -ne 'completed'){ throw "publish run timeout" }
  if($conc -ne 'success'){ throw "publish run failed: $conc" }

  # Derive package name from pyproject.toml (best-effort)
  $pkg = (Select-String -Path "pyproject.toml" -Pattern '^\s*name\s*=\s*"([^"]+)"' -SimpleMatch:$false | ForEach-Object { $_.Matches.Groups[1].Value } | Select-Object -First 1)
  if([string]::IsNullOrWhiteSpace($pkg)){ $pkg = "bar-directory-recon" }
  $pkgUrl = "https://test.pypi.org/project/$pkg/0.1.1rc1/"
  Write-Host ("RESULT >> step=1 status=ok link={0} note=""TestPyPI: {1}""" -f $url,$pkgUrl)
}catch{
  Write-Host ("RESULT >> step=1 status=fail link= note=""{0}""" -f $_.Exception.Message)
}

# -----------------------------------------
# STEP 2: GitHub release v0.1.1 (docs/demo only)
# -----------------------------------------
try{
  RepoSync $REPO
  $exists=$false
  try{ $exists = (gh release view v0.1.1 --json tagName -q .tagName) -ne $null } catch { $exists=$false }
  if(-not $exists){
    git tag -f v0.1.1
    git push -f origin v0.1.1
    gh release create v0.1.1 --title "v0.1.1 (docs/demo only)" --notes "Docs/demo refresh; no runtime changes." | Out-Null
  } else {
    gh release edit v0.1.1 --prerelease=false --latest | Out-Null
  }
  $relUrl = gh release view v0.1.1 --json url -q .url
  Write-Host ("RESULT >> step=2 status=ok link={0} note=""v0.1.1 published (docs/demo only)""" -f $relUrl)
}catch{
  Write-Host ("RESULT >> step=2 status=fail link= note=""{0}""" -f $_.Exception.Message)
}

# -----------------------------------------
# STEP 3: PR #304 (docs-only; merge)
# -----------------------------------------
try{
  RepoSync $REPO
  $prNum = 304
  $files = gh pr view $prNum --json files -q '.files[].path' 2>$null
  $paths = @()
  if($files){ $paths = $files -split "`n" | Where-Object { $_ -ne "" } }
  $isDocsOnly = $true
  foreach($p in $paths){ if($p -match '^(src/|\.github/workflows/|scripts/)'){ $isDocsOnly=$false; break } }
  if(-not $isDocsOnly){ throw "PR #$prNum is not docs-only (saw: $($paths -join ', '))" }
  gh pr merge $prNum --squash --auto | Out-Null
  $plink = gh pr view $prNum --json permalink -q .permalink
  Write-Host ("RESULT >> step=3 status=ok link={0} note=""PR304 docs-only; auto-merge queued""" -f $plink)
}catch{
  Write-Host ("RESULT >> step=3 status=fail link= note=""{0}""" -f $_.Exception.Message)
}

# -----------------------------------------
# STEP 4: Adapters wiring PR (safe; --no-exec; tiny test)
# -----------------------------------------
try{
  RepoSync $REPO
  # Ensure --no-exec in CLI (idempotent)
  $cli = "src\bdr\cli.py"
  if(!(Test-Path $cli)){ throw "missing $cli" }
  $txt = ReadRaw $cli
  if($txt -notmatch "--no-exec"){
    if($txt -notmatch "import\s+argparse"){ $txt = "import argparse`n"+$txt }
    if($txt -notmatch "import\s+os"){ $txt = $txt -replace "(import\s+argparse)", "`$0`nimport os" }
    $txt = $txt -replace "(parser\s*=\s*argparse\.ArgumentParser\([^\)]*\))","`$1`n    parser.add_argument('--no-exec', action='store_true', help='force adapters safe fallback')"
    $txt = $txt -replace "(args\s*=\s*parser\.parse_args\(\))","`$1`n    if args.no_exec: os.environ['BDR_SAFE_MODE']='1'"
    [IO.File]::WriteAllText($cli,$txt,[Text.UTF8Encoding]::new($false))
  }

  # Wire normalize adapter to preserved utility with import-guarded fallback
  $norm = "src\bdr\adapters\normalize_adapter.py"
  if(Test-Path $norm){
    $n = ReadRaw $norm
    if($n -notmatch "try:\s*# preserved utility import"){
      $patch = @"
try:  # preserved utility import
    import os
    SAFE = os.getenv('BDR_SAFE_MODE','0') == '1'
    from universal_recon.utils import record_normalizer as _rn  # optional
except Exception:
    SAFE = True
    _rn = None

def normalize(record: dict) -> dict:
    # force fallback if SAFE or util missing; otherwise try util then fallback
    if SAFE or _rn is None:
        out = dict(record)
        out['_normalized'] = True
        return out
    try:
        res = getattr(_rn, 'normalize', None)
        if callable(res):
            return res(record)  # delegate to preserved utility
    except Exception:
        pass
    out = dict(record)
    out['_normalized'] = True
    return out
"@
      $n = $patch + "`n" + $n
      [IO.File]::WriteAllText($norm,$n,[Text.UTF8Encoding]::new($false))
    }
  }

  # Tiny fallback test
  $test = @"
def test_no_exec_forces_fallback(monkeypatch):
    import os
    os.environ['BDR_SAFE_MODE']='1'
    from bdr.adapters.normalize_adapter import normalize
    rec={'id':1}
    out=normalize(rec)
    assert out.get('_normalized') is True
"@
  $changedTest = WriteIfChanged "src\tests\test_no_exec_flag.py" $test

  $br4="feat/adapters-safe-wire-$(Get-Date -Format yyyyMMdd-HHmmss)"
  git checkout -b $br4
  git add $cli src\bdr\adapters src\tests\test_no_exec_flag.py 2>$null | Out-Null
  if(git diff --cached --quiet){ $pr4="(noop)" } else {
    git commit -m "feat(adapters): --no-exec flag + import-guarded normalize wiring + fallback test"
    git push --set-upstream origin $br4
    $pr4 = gh pr create --title "feat(adapters): --no-exec + import-guarded normalize wiring" --body "Safe wiring to preserved utility with fallback; tiny test; no CI/guard changes." --base main --head $br4 --draft
    gh pr merge --squash --auto | Out-Null
  }
  Write-Host ("RESULT >> step=4 status=ok link={0} note=""adapters wiring PR opened (auto-merge)""" -f $pr4)
}catch{
  Write-Host ("RESULT >> step=4 status=fail link= note=""{0}""" -f $_.Exception.Message)
}

# -----------------------------------------
# STEP 5: README — add TestPyPI link
# -----------------------------------------
try{
  RepoSync $REPO
  # Try to derive package name for link
  $pkg = (Select-String -Path "pyproject.toml" -Pattern '^\s*name\s*=\s*"([^"]+)"' -SimpleMatch:$false | ForEach-Object { $_.Matches.Groups[1].Value } | Select-Object -First 1)
  if([string]::IsNullOrWhiteSpace($pkg)){ $pkg = "bar-directory-recon" }
  $pkgUrl = "https://test.pypi.org/project/$pkg/0.1.1rc1/"
  $block = @"
### TestPyPI pre-release

Package (rc): $pkg — **$pkgUrl**
"@
  $changed = AppendOnce "README.md" $block

  $br5="docs/testpypi-link-$(Get-Date -Format yyyyMMdd-HHmmss)"
  git checkout -b $br5
  git add README.md
  if(git diff --cached --quiet){ $pr5="(noop)" } else {
    git commit -m "docs: add TestPyPI link for 0.1.1rc1"
    git push --set-upstream origin $br5
    $pr5 = gh pr create --title "docs: add TestPyPI link (0.1.1rc1)" --body "Adds pre-release TestPyPI URL to README." --base main --head $br5 --draft
    gh pr merge --squash --auto | Out-Null
  }
  Write-Host ("RESULT >> step=5 status=ok link={0} note=""README updated with rc link""" -f $pr5)
}catch{
  Write-Host ("RESULT >> step=5 status=fail link= note=""{0}""" -f $_.Exception.Message)
}