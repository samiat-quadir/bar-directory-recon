<#
Runs the CLI demo end-to-end using the staged example dataset.
#>
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Invoke-BdrStage {
    param(
        [Parameter(Mandatory = $true)][string]$Stage,
        [string[]]$ExtraArgs = @()
    )

    Write-Host "==> $Stage"
    $cmd = @('scripts/bdr.py', $Stage) + $ExtraArgs
    $result = & python @cmd
    if ($LASTEXITCODE -ne 0) {
        throw "Stage '$Stage' failed with exit code $LASTEXITCODE. Output: $result"
    }
    return $result
}

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot '..')
Push-Location $repoRoot
try {
    $demoRoot = Join-Path '.' 'examples/demo'
    $inputPath = Join-Path $demoRoot 'input/records.json'
    $workDir = Join-Path $demoRoot 'work'
    $outputDir = Join-Path $demoRoot 'output'

    $null = New-Item -ItemType Directory -Force -Path $workDir
    $null = New-Item -ItemType Directory -Force -Path $outputDir

    $ingestedPath = Join-Path $workDir 'ingested.json'
    $normalizedPath = Join-Path $workDir 'normalized.json'
    $validationPath = Join-Path $workDir 'validation.json'
    $scorePath = Join-Path $workDir 'score.json'
    $reportJson = Join-Path $outputDir 'report.json'
    $reportMarkdown = Join-Path $outputDir 'report.md'

    Invoke-BdrStage -Stage 'ingest' -ExtraArgs @('-i', $inputPath, '-o', $ingestedPath) | Out-Null
    Invoke-BdrStage -Stage 'normalize' -ExtraArgs @('-i', $ingestedPath, '-o', $normalizedPath) | Out-Null
    Invoke-BdrStage -Stage 'validate' -ExtraArgs @('-i', $normalizedPath, '-o', $validationPath) | Out-Null
    Invoke-BdrStage -Stage 'score' -ExtraArgs @('-i', $validationPath, '-o', $scorePath) | Out-Null
    Invoke-BdrStage -Stage 'report' -ExtraArgs @('-i', $scorePath, '-o', $reportJson, '--markdown', $reportMarkdown) | Out-Null

    Write-Host "==> Demo complete. Outputs written to $outputDir"
}
finally {
    Pop-Location
}
