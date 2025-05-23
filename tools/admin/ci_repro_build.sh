#!/bin/bash
# ci_repro_build.sh
# Reproduce CI build/test in a clean temp clone
# Logs all output to logs/phase_6_build_<timestamp>.log
# Exits with code 1 on any error

set -euo pipefail

LOG_DIR="$(dirname "$0")/../../logs"
LOG_FILE="$LOG_DIR/phase_6_build_$(date +%Y%m%d_%H%M%S).log"
REPO_URL=$(git config --get remote.origin.url)
TEMP_DIR="../bar-directory-recon-temp"

mkdir -p "$LOG_DIR"

{
  echo "[INFO] Cloning repo to $TEMP_DIR: $(date)"
  rm -rf "$TEMP_DIR"
  git clone "$REPO_URL" "$TEMP_DIR"
  cd "$TEMP_DIR"

  echo "[INFO] Checking out v0.3-rc1"
  git checkout v0.3-rc1

  echo "[INFO] Creating venv and installing requirements"
  python -m venv .venv
  source .venv/bin/activate
  pip install --upgrade pip
  pip install -r requirements.txt

  echo "[INFO] Running pre-commit checks"
  pre-commit run --all-files

  echo "[INFO] Running pytest"
  pytest

  echo "[INFO] CI reproduction build complete: $(date)"
  echo "[INFO] Fetching origin/main and dry-running merge into prep/phase-28-merge"
  git fetch origin main
  git checkout prep/phase-28-merge
  MERGE_LOG="$LOG_DIR/phase_6_merge_dryrun_$(date +%Y%m%d_%H%M%S).log"
  git merge --no-commit --no-ff origin/main > "$MERGE_LOG" 2>&1 || git merge --abort
} > "$LOG_FILE" 2>&1 || { echo "[ERROR] CI reproduction build failed, see $LOG_FILE" | tee -a "$LOG_FILE"; exit 1; }

exit 0
