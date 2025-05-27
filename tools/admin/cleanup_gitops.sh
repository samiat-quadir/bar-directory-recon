#!/bin/bash
# cleanup_gitops.sh
# Automated git branch and tag cleanup for bar-directory-recon-new
# Logs all actions to logs/phase_5/phase_5_branch_tag_cleanup_$(date +%Y%m%d_%H%M%S).log
# Exits with code 1 on any error

set -euo pipefail

LOG_DIR="$(dirname "$0")/../../logs/phase_5"
LOG_FILE="$LOG_DIR/phase_5_branch_tag_cleanup_$(date +%Y%m%d_%H%M%S).log"

mkdir -p "$LOG_DIR"
exec > >(tee -a "$LOG_FILE") 2>&1

echo "[INFO] Starting git branch and tag cleanup: $(date)"

git fetch --all --prune || { echo "[ERROR] git fetch failed"; exit 1; }

echo "[INFO] Listing local branches for cleanup..."
# List branches matching patterns, except feature/phase-28-dashboard-init
BRANCHES=$(git for-each-ref --format='%(refname:short)' refs/heads/ |
  grep -E '^(feature/old-|bugfix/.+-wip)' |
  grep -v '^feature/phase-28-dashboard-init$')

for branch in $BRANCHES; do
  echo "[INFO] Deleting branch: $branch"
  git branch -D "$branch" || { echo "[ERROR] Failed to delete branch $branch"; exit 1; }
done

echo "[INFO] Listing tags for cleanup..."
# Delete tags older than 30 days or matching rc-* if superseded
NOW=$(date +%s)
TAGS_TO_DELETE=""
for tag in $(git tag); do
  TAG_DATE=$(git log -1 --format=%ct "$tag" 2>/dev/null || echo 0)
  AGE=$(( (NOW - TAG_DATE) / 86400 ))
  if [[ $AGE -gt 30 ]]; then
    TAGS_TO_DELETE+="$tag\n"
  fi
  # If rc-* and a newer tag exists, mark for deletion
  if [[ "$tag" =~ ^rc- ]]; then
    BASE=${tag#rc-}
    for newer in $(git tag --sort=-creatordate | grep "^$BASE$"); do
      if [[ "$newer" != "$tag" ]]; then
        TAGS_TO_DELETE+="$tag\n"
        break
      fi
    done
  fi
done

echo -e "$TAGS_TO_DELETE" | sort -u | while read -r tag; do
  [[ -z "$tag" ]] && continue
  echo "[INFO] Deleting tag: $tag"
  git tag -d "$tag" || { echo "[ERROR] Failed to delete tag $tag"; exit 1; }
done

# --- GIT GC, REFS, FSCK ---
GC_LOG="$LOG_DIR/phase_5_gc_$(date +%Y%m%d_%H%M%S).log"

{
  echo "[INFO] Starting git reflog/gc/fsck: $(date)"
  git reflog expire --expire=now --all
  git gc --prune=now --aggressive
  git fsck --unreachable --no-progress
  echo "[INFO] Git gc/fsck complete: $(date)"
} > >(tee -a "$GC_LOG") 2>&1 || { echo "[ERROR] git gc/fsck failed, see $GC_LOG" | tee -a "$GC_LOG"; exit 1; }

# --- GIT FSCK FULL & LOG GRAPH ---
FSCK_LOG="$LOG_DIR/phase_5_fsck_$(date +%Y%m%d_%H%M%S).log"
GRAPH_LOG="$LOG_DIR/phase_5_graph_$(date +%Y%m%d_%H%M%S).log"

# Run git fsck --full and check for errors
{
  echo "[INFO] Running git fsck --full: $(date)"
  git fsck --full
} > "$FSCK_LOG" 2>&1

if grep -q "error:" "$FSCK_LOG"; then
  echo "[ERROR] git fsck --full found errors. See $FSCK_LOG" | tee -a "$FSCK_LOG"
  exit 2
fi

echo "[INFO] Running git log --oneline --graph --decorate --all: $(date)" | tee -a "$GRAPH_LOG"
git log --oneline --graph --decorate --all > "$GRAPH_LOG" 2>&1

# --- BRANCH/TAG/PUSH FINALIZATION ---
PUSH_LOG="$LOG_DIR/phase_5_push_$(date +%Y%m%d_%H%M%S).log"

{
  echo "[INFO] Checking for prep/phase-28-merge branch: $(date)"
  if git show-ref --verify --quiet refs/heads/prep/phase-28-merge; then
    echo "[INFO] Branch prep/phase-28-merge already exists."
  else
    echo "[INFO] Creating branch prep/phase-28-merge from feature/phase-28-dashboard-init."
    git branch prep/phase-28-merge feature/phase-28-dashboard-init
  fi

  echo "[INFO] Tagging HEAD with v0.3-rc1 (force)."
  git tag -f v0.3-rc1

  echo "[INFO] Pushing changes to origin with --prune and --follow-tags."
  git push origin --prune --follow-tags
} > "$PUSH_LOG" 2>&1 || { echo "[ERROR] Branch/tag/push step failed, see $PUSH_LOG" | tee -a "$PUSH_LOG"; exit 1; }

# --- TRIGGER GITHUB CI WORKFLOW ---
CI_LOG="$LOG_DIR/phase_5_ci_trigger_$(date +%Y%m%d_%H%M%S).log"

# Try to trigger the primary workflow using GitHub CLI (gh)
REPO_URL=$(git config --get remote.origin.url)
REPO_SLUG=$(basename "${REPO_URL%.git}")
REPO_OWNER=$(basename $(dirname "$REPO_URL"))
REPO_FULL="$REPO_OWNER/$REPO_SLUG"

# Find the default branch
default_branch=$(git remote show origin | awk '/HEAD branch/ {print $NF}')

# Trigger the workflow and log the response
{
  echo "[INFO] Triggering GitHub Actions workflow for $REPO_FULL on $default_branch: $(date)"
  gh workflow run --repo "$REPO_FULL" --ref "$default_branch" --json > /tmp/gh_workflow_response.json 2>&1
  cat /tmp/gh_workflow_response.json
} > "$CI_LOG" 2>&1 || { echo "[ERROR] CI workflow trigger failed, see $CI_LOG" | tee -a "$CI_LOG"; exit 1; }

echo "[INFO] Cleanup complete: $(date)"
exit 0
