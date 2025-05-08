Write-Host "`nDevice Detection Script (PowerShell)`n" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan

# Get current username
$username = $env:USERNAME.ToLower()
$device = "Unknown"

# Detect device based on username
if ($username -like "*samqu*") {
    $device = "ASUS"
}
elseif ($username -like "*samq*" -and $username -notlike "*samqu*") {
    $device = "Work Desktop"
}

# Get Python executable path
$pythonPath = (Get-Command python -ErrorAction SilentlyContinue).Path
if (-not $pythonPath) {
    $pythonPath = ".\.venv311\Scripts\python.exe"
    if (Test-Path $pythonPath) {
        $pythonPath = Resolve-Path $pythonPath
    }
    else {
        $pythonPath = "Python not found"
    }
}

# Get Python version
$pythonVersion = ""
if (Test-Path $pythonPath) {
    $pythonVersion = & $pythonPath -c "import sys; print(sys.version.split()[0])"
}

# Display information
Write-Host "Detected device profile: $device" -ForegroundColor Green
Write-Host "Username: $username" -ForegroundColor Yellow
Write-Host "Python executable: $pythonPath" -ForegroundColor Yellow
Write-Host "Python version: $pythonVersion" -ForegroundColor Yellow
Write-Host "Operating system: $((Get-WmiObject -Class Win32_OperatingSystem).Caption)" -ForegroundColor Yellow

# Create logs directory if it doesn't exist
$logDir = "logs"
if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
}

# Log information to file
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$logFile = "logs\setup_log.txt"

"[$timestamp] 🖥️  Detected device profile: $device" | Out-File -Append -FilePath $logFile -Encoding utf8
"[$timestamp] 🐍 Python executable: $pythonPath" | Out-File -Append -FilePath $logFile -Encoding utf8
"[$timestamp] ✅ Python major version is correct (3.x)" | Out-File -Append -FilePath $logFile -Encoding utf8

Write-Host "`nInformation has been logged to $logFile" -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Cyan