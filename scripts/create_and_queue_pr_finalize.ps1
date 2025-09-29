Set-Location 'C:\Code\bar-directory-recon'
$branch = (git rev-parse --abbrev-ref HEAD).Trim()
if($branch -ne 'chore/attic-sweep-20250929'){ Write-Output "WARN: expected branch chore/attic-sweep-20250929 but on $branch" }
try {
  $prCreate = gh pr create -f -d -t "chore(attic): quarantine non-core + scope coverage" -b "Preserve all files on branch attic-20250929. Remove device/experiment files from main; add .coveragerc to measure core only." 2>&1
  Write-Output "PR_CREATE_OUTPUT: $prCreate"
  $prUrl = gh pr view --json url -q ".url" 2>$null
  if([string]::IsNullOrWhiteSpace($prUrl)){
    # fallback to constructing the web-new PR creation URL
    $prUrl = "https://github.com/samiat-quadir/bar-directory-recon/pull/new/chore/attic-sweep-20250929"
    Write-Output "PR_URL_FALLBACK=$prUrl"
  }
  Set-Content -Path pr_finalize.txt -Value $prUrl -Encoding utf8
  try {
    gh pr merge $prUrl --squash --auto 2>&1 | Write-Output
    Write-Output "MERGE_COMMAND_SENT"
  } catch {
    Write-Output "MERGE_COMMAND_FAILED: $_"
  }
} catch {
  Write-Output "GH_PR_CREATE_FAILED: $_"
  $fallback = "https://github.com/samiat-quadir/bar-directory-recon/pull/new/chore/attic-sweep-20250929"
  Set-Content -Path pr_finalize.txt -Value $fallback -Encoding utf8
}
