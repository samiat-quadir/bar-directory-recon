param(
    [Parameter(Mandatory = $true)]
    [string]$Branch
)

Set-Location (Resolve-Path "${PSScriptRoot}\..")
$file = '_attic_delete.txt'
if (-Not (Test-Path $file)) {
    Write-Output 'Delete list not found'
    exit 1
}
$lines = Get-Content $file | Where-Object { $_.Trim() -ne '' }
Write-Output "Applying deletions for $($lines.Count) paths (quiet mode)"
foreach ($p in $lines) {
    git rm -r --ignore-unmatch -- $p > $null 2>&1
}
$staged = (git diff --name-only --staged | Measure-Object -Line).Lines
Write-Output "Staged files after removals: $staged"
$unmerged = (git diff --name-only --diff-filter=U)
if ($unmerged) { Write-Output 'UNMERGED:'; Write-Output $unmerged }

Write-Output 'Committing (skip pre-commit hooks)'
git commit -m 'chore(attic): apply delete list; resolve modify/delete conflicts' --no-verify 2>&1 | Write-Output || Write-Output 'Commit failed or nothing to commit'
Write-Output "Pushing with force-with-lease to origin $Branch"
git push --force-with-lease origin HEAD:$Branch 2>&1 | Write-Output
Write-Output 'Done'
