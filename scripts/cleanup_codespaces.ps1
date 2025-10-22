Param()
$ErrorActionPreference = 'Stop'
Write-Output "Listing codespaces for repo..."
$json = gh codespace list -R samiat-quadir/bar-directory-recon --json name, displayName, state 2>$null | Out-String
if (-not $json) { Write-Output "No codespaces found or gh returned no output."; exit 0 }
$entries = ConvertFrom-Json $json
foreach ($e in $entries) {
    if ($e.name -like 'bdr-smoke*' -or $e.displayName -like 'bdr-smoke*') {
        try {
            Write-Output "Stopping codespace $($e.name) ($($e.displayName)) state=$($e.state)"
            gh codespace stop -c $e.name
        }
        catch {
            Write-Output "Failed stopping $($e.name): $($_.Exception.Message)"
        }
    }
}
Write-Output "Cleanup complete."
