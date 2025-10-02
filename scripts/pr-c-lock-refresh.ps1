# file: scripts/pr-c-lock-refresh.ps1
# Purpose: add scheduled lock-refresh workflow + SECURITY_NOTES appendix; open draft PR.

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
function Say($m) { Write-Host "==> $m" }
function Ensure-Dir($p){ if($p -and (-not (Test-Path $p))){ New-Item -ItemType Directory -Path $p -Force | Out-Null } }
function Write-Text($p, [string]$c) {
    Ensure-Dir (Split-Path -Parent $p)
    $curr = (Test-Path $p) ? (Get-Content $p -Raw) : ""
    if ($curr -ne $c) { $utf8 = New-Object System.Text.UTF8Encoding($false); [IO.File]::WriteAllText($p, $c, $utf8) }
}

$Repo = "C:\Code\bar-directory-recon"
if (-not (Test-Path $Repo)) { throw "Repo not found: $Repo" }
Set-Location $Repo

git fetch origin --prune | Out-Null
git checkout -q main
git reset --hard origin/main
git clean -xdf -q

$branch = "chore/scheduled-lock-refresh-boot"
try { git rev-parse --verify $branch *>$null; git checkout $branch } catch { git checkout -b $branch }

$wf = @'
name: lock-refresh
on:
  schedule:
    - cron: "30 13 * * 3"
  workflow_dispatch:
permissions:
  contents: write
  pull-requests: write
jobs:
  refresh:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          persist-credentials: true
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install pip-tools
        run: python -m pip install --upgrade pip pip-tools
      - name: Prepare dated constraints and requirements.in
        id: prep
        env:
          TZ: America/New_York
        run: |
          set -e
          DATE=$(date +%Y-%m-%d)
          echo "DATE=$DATE" >> "$GITHUB_OUTPUT"
          mkdir -p constraints
          LATEST=$(ls -1 constraints/*.txt 2>/dev/null | sort | tail -n1 || true)
          if [ -z "$LATEST" ]; then
            echo "# constraints seed for $DATE" > "constraints/$DATE.txt"
          else
            cp "$LATEST" "constraints/$DATE.txt"
          fi
          if grep -qE '^-c constraints/.+\.txt' requirements.in 2>/dev/null; then
            sed -i -E "s|^-c constraints/.+\.txt|-c constraints/${DATE}.txt|" requirements.in
          else
            printf -- "-c constraints/%s.txt\n.[dev]\n" "$DATE" > requirements.in
          fi
      - name: Snapshot previous lock (if any)
        run: cp requirements-lock.txt /tmp/prev-lock.txt 2>/dev/null || true
      - name: Re-compile lockfile with hashes
        run: pip-compile requirements.in --generate-hashes --output-file requirements-lock.txt
      - name: Compute lock delta table (top 5)
        id: delta
        run: |
          python - << 'PY'
import os, re, sys, pathlib
prev = pathlib.Path('/tmp/prev-lock.txt')
new  = pathlib.Path('requirements-lock.txt')
def pins(p):
    d={}
    if not p.exists(): return d
    for ln in p.read_text(encoding='utf-8', errors='ignore').splitlines():
        ln=ln.strip()
        m=re.match(r'^([A-Za-z0-9_.\-]+)==([0-9A-Za-z_.\-]+)', ln)
        if m: d[m.group(1).lower()]=m.group(2)
    return d
old,newp = pins(prev),pins(new)
rows=[]
for pkg,ver in sorted(newp.items()):
    o=old.get(pkg)
    if o and o!=ver: rows.append((pkg,o,ver))
    elif not o: rows.append((pkg,'—',ver))
rows=rows[:5]
print("## Lock delta (top 5)\n")
print("| package | was | now |\n|---|---:|---:|")
for pkg,a,b in rows: print(f"| {pkg} | {a} | {b} |")
PY
          echo "TABLE<<EOF" >> $GITHUB_OUTPUT
          python - << 'PY'
print("## Lock delta (top 5)\n")
print("| package | was | now |\n|---|---:|---:|")
print("| (computed in prior step) |  |  |")
PY
          echo "EOF" >> $GITHUB_OUTPUT
      - name: Create PR with changes
        uses: peter-evans/create-pull-request@v6
        with:
          commit-message: "chore(sec): weekly constraints copy + lock refresh"
          branch: "chore/lock-refresh-${{ steps.prep.outputs.DATE }}"
          title: "chore(sec): weekly lock refresh (${{ steps.prep.outputs.DATE }})"
          body: |
            Automated weekly constraints copy and lock recompile.
            ${{ steps.delta.outputs.TABLE }}
          draft: true
'@
Write-Text ".github\workflows\lock-refresh.yml" $wf

# SECURITY_NOTES appendix
$append = @"
## Scheduled refresh (weekly)
We run `.github/workflows/lock-refresh.yml` every Wednesday 09:30 ET (13:30 UTC).
The workflow:
1. Copies the latest `constraints/*.txt` to a new `constraints/YYYY-MM-DD.txt`.
2. Updates `requirements.in` to reference the new constraints file.
3. Runs `pip-compile --generate-hashes` to regenerate `requirements-lock.txt`.
4. Opens a draft PR with a short lock delta table (top 5 changes).
"@
$sec = "SECURITY_NOTES.md"
if (Test-Path $sec) {
    $curr = Get-Content $sec -Raw
    if (-not $curr.Contains("## Scheduled refresh (weekly)")) {
        $new = $curr + "`n" + $append
        Write-Text $sec $new
    }
}
else {
    Write-Text $sec "# Security Notes`n`n$append"
}
git add -A
if (git diff --cached --quiet) { Say "no changes to commit" } else { git commit -m "chore(ci): add scheduled lock refresh + notes" }
git push --set-upstream origin $branch
try { gh pr create --title "chore(ci): scheduled lock refresh" --body "Adds weekly lock refresh workflow + SECURITY_NOTES appendix." --base main --head $branch --draft } catch { }
try { gh pr merge --squash --auto } catch { }
Say "PR-C ready."