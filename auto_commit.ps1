# auto_commit.ps1
cd "C:\Users\samqu\OneDrive - Digital Age Marketing Group\Desktop\Local Py\Work Projects\bar-directory-recon"

# Optional: pull if you have a remote
# git pull origin main

# Stage all changes
git add .

# Create commit message with timestamp
$timestamp = (Get-Date).ToString("yyyy-MM-dd_HH-mm-ss")
$commitMsg = "Auto snapshot commit at $timestamp"

# Create the commit
git commit -m $commitMsg

# Optional: push to remote
git push origin main

Compress-Archive -Path "C:\...\universal_recon\*" -DestinationPath "C:\...\universal_recon\universal_recon_%($timestamp).zip"
git add universal_recon_%($timestamp).zip
git commit -m "Adding daily snapshot zip at $timestamp"
