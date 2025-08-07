# VS Code Git Workflow Fixer
# Prevents "Publish Branch" prompts and manual merge issues

Write-Host "[*] VS Code Git Workflow Fixer" -ForegroundColor Cyan
Write-Host "[*] Preventing 'Publish Branch' prompts and manual merges..." -ForegroundColor Yellow

# Get current branch
$currentBranch = git branch --show-current
if (-not $currentBranch) {
    Write-Host "[-] Could not determine current branch" -ForegroundColor Red
    exit 1
}

Write-Host "[*] Current branch: $currentBranch" -ForegroundColor White

# Check if remote branch exists
$remoteExists = git ls-remote --heads origin $currentBranch 2>$null
if ($remoteExists) {
    Write-Host "[+] Remote branch exists" -ForegroundColor Green

    # Check if upstream tracking is set
    $upstream = git config --get "branch.$currentBranch.remote" 2>$null
    if ($upstream -eq "origin") {
        Write-Host "[+] Upstream tracking already configured" -ForegroundColor Green
    }
    else {
        Write-Host "[!] Setting up upstream tracking..." -ForegroundColor Yellow
        git branch --set-upstream-to=origin/$currentBranch $currentBranch
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[+] Upstream tracking configured successfully!" -ForegroundColor Green
        }
    }
}
else {
    Write-Host "[!] Remote branch doesn't exist - creating it..." -ForegroundColor Yellow

    # Add and commit any changes first
    $status = git status --porcelain
    if ($status) {
        Write-Host "[*] Committing current changes..." -ForegroundColor White
        git add .
        git commit -m "Auto-commit: Setup branch tracking and prevent VS Code publish prompts"
    }

    # Create remote branch with upstream tracking
    git push -u origin $currentBranch
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[+] Remote branch created with upstream tracking!" -ForegroundColor Green
    }
    else {
        Write-Host "[-] Failed to create remote branch" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "[+] SUCCESS: VS Code workflow fixed!" -ForegroundColor Green
Write-Host "[*] You can now:" -ForegroundColor White
Write-Host "    - Use Ctrl+Shift+P > Git: Push normally" -ForegroundColor White
Write-Host "    - No more 'Publish Branch' prompts" -ForegroundColor White
Write-Host "    - No more manual merge requirements" -ForegroundColor White

# Test the setup
Write-Host ""
Write-Host "[*] Testing the setup..." -ForegroundColor Yellow
$trackingBranch = git config --get "branch.$currentBranch.merge"
if ($trackingBranch) {
    Write-Host "[+] Tracking branch: $trackingBranch" -ForegroundColor Green
    Write-Host "[+] Setup verified successfully!" -ForegroundColor Green
}
else {
    Write-Host "[!] Warning: Tracking may not be fully configured" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
