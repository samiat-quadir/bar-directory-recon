#!/usr/bin/env bash

# bar-directory-recon Export Wrapper
# Purpose: Validate environment, run health check, execute export, log results
# Usage: bash run_export.sh <csv_path> <sheet_id> [--mode append|replace] [--worksheet name]

set -e  # Exit on error

CSV_PATH="${1}"
SHEET_ID="${2}"
MODE="${3:-append}"
WORKSHEET="${4:-leads}"

echo "=========================================="
echo "bdr Export Wrapper (v0.1.9)"
echo "=========================================="
echo "CSV: ${CSV_PATH}"
echo "Sheet ID: ${SHEET_ID}"
echo "Mode: ${MODE}"
echo "Worksheet: ${WORKSHEET}"
echo ""

# 1. Validate Python 3.11+
echo "[1/4] Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ $PYTHON_MAJOR -lt 3 ] || ([ $PYTHON_MAJOR -eq 3 ] && [ $PYTHON_MINOR -lt 11 ]); then
    echo "❌ Python 3.11+ required (found: $PYTHON_VERSION)"
    exit 1
fi
echo "✅ Python $PYTHON_VERSION"
echo ""

# 2. Run health check
echo "[2/4] Running bdr doctor --no-exec..."
if ! bdr doctor --no-exec > /tmp/bdr_doctor.log 2>&1; then
    echo "❌ Health check failed. See /tmp/bdr_doctor.log"
    cat /tmp/bdr_doctor.log
    exit 1
fi

if ! grep -q "Overall: PASS" /tmp/bdr_doctor.log; then
    echo "❌ Doctor output shows failures:"
    cat /tmp/bdr_doctor.log
    exit 1
fi
echo "✅ Health check passed"
echo ""

# 3. Validate CSV exists
echo "[3/4] Validating CSV..."
if [ ! -f "$CSV_PATH" ]; then
    echo "❌ CSV file not found: $CSV_PATH"
    exit 1
fi

ROWS=$(wc -l < "$CSV_PATH")
echo "✅ CSV found: $ROWS rows"
echo ""

# 4. Run export
echo "[4/4] Running export..."
echo "Command: bdr export csv-to-sheets $CSV_PATH --sheet-id $SHEET_ID --worksheet $WORKSHEET --mode $MODE"
echo ""

if bdr export csv-to-sheets "$CSV_PATH" \
    --sheet-id "$SHEET_ID" \
    --worksheet "$WORKSHEET" \
    --mode "$MODE"; then
    echo ""
    echo "=========================================="
    echo "✅ Export completed successfully"
    echo "=========================================="
    echo "Rows exported: $ROWS"
    echo "Destination: https://docs.google.com/spreadsheets/d/$SHEET_ID"
    echo "Worksheet: $WORKSHEET"
    echo ""
    exit 0
else
    echo ""
    echo "=========================================="
    echo "❌ Export failed"
    echo "=========================================="
    exit 1
fi
