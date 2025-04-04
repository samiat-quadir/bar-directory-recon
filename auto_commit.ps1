# Make sure you're in the correct directory
cd "C:\Users\samqu\OneDrive - Digital Age Marketing Group\Desktop\Local Py\Work Projects\bar-directory-recon"

# Optional: Pull latest if you’re on a remote Git (skip if local only)
# git pull origin main

# Stage all changed files
git add .

# Generate a commit message with timestamp
$timestamp = (Get-Date).ToString("yyyy-MM-dd_HH-mm-ss")
$commitMsg = "Auto snapshot commit at $timestamp"

# Create the commit
git commit -m $commitMsg

# Optional: push if you have a remote set
# git push origin main
