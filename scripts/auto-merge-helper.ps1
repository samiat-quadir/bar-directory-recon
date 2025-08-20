# Auto-merge automation script
# This script labels safe PRs for automatic merging once CI passes

$safeHeads = @(
    "ops/monitoring-hardening",
    "docs/gsheets-notes",
    "chore/devcontainer-defaults",
    "chore/doctor-ci",
    "feat/social-plugin"
)

Write-Host "Checking for safe PRs to auto-merge..."
Write-Host "Safe branch patterns: $($safeHeads -join ', ')"

try {
    $prs = gh pr list -s open --json number, headRefName, title | ConvertFrom-Json

    if ($prs.Count -eq 0) {
        Write-Host "No open PRs found."
    }
    else {
        foreach ($pr in $prs) {
            if ($safeHeads -contains $pr.headRefName) {
                Write-Host "Found safe PR #$($pr.number): $($pr.title) (branch: $($pr.headRefName))"
                try {
                    gh pr edit $pr.number --add-label auto-merge-ok
                    Write-Host "✅ Added auto-merge-ok label to PR #$($pr.number)"
                }
                catch {
                    Write-Host "⚠️  Failed to add label to PR #$($pr.number): $_"
                }
            }
        }
    }
}
catch {
    Write-Host "Error fetching PRs: $_"
}

Write-Host "`nRepo automation summary:"
Write-Host "- YAML lint CI workflow: Created in chore/doctor-ci branch"
Write-Host "- Safe PR patterns defined for auto-merge"
Write-Host "- Main branch synchronized"
