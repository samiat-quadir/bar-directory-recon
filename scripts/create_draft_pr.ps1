# Push current branch and create a draft PR via gh; write the PR url to pr.txt
Set-Location 'C:\Code\bar-directory-recon'
$branch = (git rev-parse --abbrev-ref HEAD).Trim()
if($branch -match 'chore/attic-sweep-(\d{8})'){ $TS = $Matches[1] } else { $TS = (Get-ChildItem -Path .git\refs\heads -ErrorAction SilentlyContinue | Where-Object { $_.Name -match 'attic-\d{8}' } | Select-Object -First 1).Name }
try {
  git push -u origin HEAD
} catch {
  Write-Output "git push failed: $_"
}
$pct = (Get-Content pct.txt -Raw).Trim()
try {
  $prOutput = gh pr create -f -d -t "chore(attic): quarantine non-core + scope coverage" -b "Preserve all files on branch attic-$TS. Remove device/experiment files from main; add .coveragerc to measure core only. Local coverage $pct%."
  $prUrl = gh pr view --json url -q ".url"
  Set-Content -Path pr.txt -Value $prUrl
  Write-Output "PR_CREATED=$prUrl"
} catch {
  Write-Output "GH_PR_FAILED: $_"
  Set-Content -Path pr.txt -Value ""
}
