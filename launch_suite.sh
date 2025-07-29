#!/bin/bash
# Launch Suite for Bar Directory Recon - Bash Version
#
# This script provides a complete launch suite for the bar directory reconnaissance
# automation system. It handles environment activation, configuration loading,
# and starts all required services.
#
# Usage:
#   ./launch_suite.sh [mode] [sites]
#   ./launch_suite.sh full
#   ./launch_suite.sh dashboard
#   ./launch_suite.sh demo
#   ./launch_suite.sh async-demo site1.com,site2.com
#
# Author: Bar Directory Recon Team
# Version: 2.0
# Last Modified: July 25, 2025

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
GRAY='\033[0;37m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}$1${NC}"
}

log_success() {
    echo -e "${GREEN}$1${NC}"
}

log_warning() {
    echo -e "${YELLOW}$1${NC}"
}

log_error() {
    echo -e "${RED}$1${NC}"
}

log_cyan() {
    echo -e "${CYAN}$1${NC}"
}

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

# Parse arguments
MODE="${1:-full}"
SITES="${2:-}"

# Validate mode
case "$MODE" in
    full|dashboard|demo|env-check|async-demo|help)
        ;;
    *)
        log_error "Invalid mode: $MODE"
        echo "Valid modes: full, dashboard, demo, env-check, async-demo, help"
        exit 1
        ;;
esac

# Display help
if [ "$MODE" = "help" ]; then
    echo "Launch Suite for Bar Directory Recon"
    echo ""
    echo "Usage: $0 [mode] [sites]"
    echo ""
    echo "Modes:"
    echo "  full       - Complete launch suite (default)"
    echo "  dashboard  - Dashboard server only"
    echo "  demo       - Automation demo"
    echo "  async-demo - Async pipeline demo"
    echo "  env-check  - Environment validation"
    echo "  help       - This help message"
    echo ""
    echo "Examples:"
    echo "  $0 full"
    echo "  $0 dashboard"
    echo "  $0 async-demo site1.com,site2.com"
    exit 0
fi

# Header
log_cyan "🚀 Bar Directory Recon - Launch Suite (Bash)"
echo "============================================================"
log_warning "📁 Project Root: $PROJECT_ROOT"
log_success "🎯 Launch Mode: $MODE"

# Step 1: Activate Virtual Environment
log_info ""
log_info "🔧 Step 1: Activating Python Virtual Environment..."

VENV_PATH="$PROJECT_ROOT/.venv"
VENV_ACTIVATE="$VENV_PATH/bin/activate"

if [ -f "$VENV_ACTIVATE" ]; then
    echo "Found virtual environment at: $VENV_PATH"
    source "$VENV_ACTIVATE"

    if [ $? -eq 0 ]; then
        log_success "✅ Virtual environment activated successfully"
    else
        log_error "❌ Failed to activate virtual environment"
        exit 1
    fi
else
    log_warning "⚠️ Virtual environment not found at: $VENV_PATH"
    log_warning "   Creating virtual environment..."

    # Create virtual environment
    python3 -m venv "$VENV_PATH"
    if [ $? -eq 0 ]; then
        log_success "✅ Virtual environment created"
        source "$VENV_ACTIVATE"
    else
        log_error "❌ Failed to create virtual environment"
        exit 1
    fi
fi

# Verify Python is available
PYTHON_VERSION=$(python --version 2>&1)
log_cyan "🐍 Python Version: $PYTHON_VERSION"

# Step 2: Load Environment Configuration
log_info ""
log_info "🔧 Step 2: Loading Environment Configuration..."

ENV_LOADER_PATH="$PROJECT_ROOT/env_loader.py"
if [ -f "$ENV_LOADER_PATH" ]; then
    echo "Running environment loader: $ENV_LOADER_PATH"
    python "$ENV_LOADER_PATH"

    if [ $? -eq 0 ]; then
        log_success "✅ Environment configuration loaded successfully"
    else
        log_warning "⚠️ Environment loader completed with warnings"
    fi
else
    log_warning "⚠️ Environment loader not found, using system environment"
fi

# Step 3: Execute based on mode
log_info ""
log_info "🎯 Step 3: Executing Launch Mode: $MODE"

case "$MODE" in
    full)
        log_success "🚀 Starting Full Launch Suite..."

        # Start async pipeline demo
        log_cyan ""
        log_cyan "📊 Starting Async Pipeline Demo..."
        ASYNC_DEMO_PATH="$PROJECT_ROOT/async_pipeline_demo.py"
        if [ -f "$ASYNC_DEMO_PATH" ]; then
            if [ -n "$SITES" ]; then
                IFS=',' read -ra SITE_ARRAY <<< "$SITES"
                python "$ASYNC_DEMO_PATH" --sites "${SITE_ARRAY[@]}"
            else
                python "$ASYNC_DEMO_PATH" --demo-mode
            fi
        else
            log_warning "⚠️ Async pipeline demo not found"
        fi

        # Start dashboard server
        log_cyan ""
        log_cyan "🖥️ Starting Dashboard Server..."
        DASHBOARD_PATH="$PROJECT_ROOT/automation/dashboard.py"
        if [ -f "$DASHBOARD_PATH" ]; then
            python "$DASHBOARD_PATH" &
            DASHBOARD_PID=$!
            log_success "✅ Dashboard server started (PID: $DASHBOARD_PID)"
        else
            log_warning "⚠️ Dashboard server not found"
        fi
        ;;

    dashboard)
        log_success "🖥️ Starting Dashboard Only..."

        DASHBOARD_PATH="$PROJECT_ROOT/automation/dashboard.py"
        if [ -f "$DASHBOARD_PATH" ]; then
            python "$DASHBOARD_PATH"
        else
            log_error "❌ Dashboard not found at: $DASHBOARD_PATH"
            exit 1
        fi
        ;;

    demo)
        log_success "🎬 Starting Demo Mode..."

        DEMO_PATH="$PROJECT_ROOT/automation_demo.py"
        if [ -f "$DEMO_PATH" ]; then
            python "$DEMO_PATH"
        else
            log_error "❌ Demo script not found at: $DEMO_PATH"
            exit 1
        fi
        ;;

    async-demo)
        log_success "⚡ Starting Async Pipeline Demo..."

        ASYNC_DEMO_PATH="$PROJECT_ROOT/async_pipeline_demo.py"
        if [ -f "$ASYNC_DEMO_PATH" ]; then
            if [ -n "$SITES" ]; then
                IFS=',' read -ra SITE_ARRAY <<< "$SITES"
                python "$ASYNC_DEMO_PATH" --sites "${SITE_ARRAY[@]}" --sync-vs-async
            else
                python "$ASYNC_DEMO_PATH" --sync-vs-async
            fi
        else
            log_error "❌ Async demo not found at: $ASYNC_DEMO_PATH"
            exit 1
        fi
        ;;

    env-check)
        log_success "🔍 Environment Check Mode..."

        # Check Python environment
        log_cyan ""
        log_cyan "🐍 Python Environment:"
        python -c "import sys; print(f'Python: {sys.version}'); print(f'Executable: {sys.executable}')"

        # Check virtual environment
        if [ -n "$VIRTUAL_ENV" ]; then
            log_success "✅ Virtual Environment: $VIRTUAL_ENV"
        else
            log_warning "⚠️ No virtual environment detected"
        fi

        # Check key modules
        log_cyan ""
        log_cyan "📦 Module Check:"
        MODULES=("requests" "selenium" "pandas" "pydantic" "yaml")
        for MODULE in "${MODULES[@]}"; do
            if python -c "import $MODULE" 2>/dev/null; then
                log_success "✅ $MODULE: Available"
            else
                log_error "❌ $MODULE: Not available"
            fi
        done

        # Check project structure
        log_cyan ""
        log_cyan "📁 Project Structure:"
        REQUIRED_DIRS=("automation" "tools" "scripts" "config" "logs")
        for DIR in "${REQUIRED_DIRS[@]}"; do
            DIR_PATH="$PROJECT_ROOT/$DIR"
            if [ -d "$DIR_PATH" ]; then
                log_success "✅ $DIR/: Present"
            else
                log_error "❌ $DIR/: Missing"
            fi
        done
        ;;
esac

# Step 4: Launch Summary
log_info ""
log_info "📊 Launch Summary:"
echo "  Mode: $MODE"
echo "  Project Root: $PROJECT_ROOT"
if [ -n "$SITES" ]; then
    echo "  Sites: $SITES"
fi
log_success "  Status: Launch completed"

log_success ""
log_success "🎉 Launch Suite execution completed!"
log_cyan "💡 Use './launch_suite.sh help' for more options"
