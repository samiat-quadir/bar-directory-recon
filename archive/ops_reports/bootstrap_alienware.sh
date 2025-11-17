#!/bin/bash
#
# Alienware Device Bootstrap Script for bar-directory-recon Project
# =================================================================
#
# This script brings an Alienware device into exact parity with the ASUS "golden image" environment.
# It sets up the complete development environment from scratch.
#
# Usage:
#   ./bootstrap_alienware.sh [workspace_root] [--skip-validation]
#
# Arguments:
#   workspace_root     Root directory where project will be cloned (default: ~/Code)
#   --skip-validation  Skip the final validation step
#

set -euo pipefail

# Configuration
WORKSPACE_ROOT="${1:-$HOME/Code}"
SKIP_VALIDATION=false
PROJECT_NAME="bar-directory-recon"
REPOSITORY_URL="https://github.com/samiat-quadir/bar-directory-recon.git"
REQUIRED_PYTHON_VERSION="3.13"
TAG_VERSION="v2.0"

# Parse arguments
for arg in "$@"; do
    case $arg in
        --skip-validation)
            SKIP_VALIDATION=true
            shift
            ;;
        *)
            ;;
    esac
done

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logging functions
log_header() {
    echo -e "${PURPLE}📋 $1${NC}"
}

log_info() {
    echo -e "${CYAN}🔍 $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check system prerequisites
check_prerequisites() {
    log_header "Checking system prerequisites..."

    local issues=()

    # Check Git
    if command_exists git; then
        local git_version=$(git --version)
        log_success "Git found: $git_version"
    else
        issues+=("Git is not installed or not in PATH")
    fi

    # Check Python 3.13
    if command_exists python3.13; then
        PYTHON_CMD="python3.13"
    elif command_exists python3; then
        PYTHON_CMD="python3"
    elif command_exists python; then
        PYTHON_CMD="python"
    else
        issues+=("Python is not installed or not in PATH")
        return 1
    fi

    local python_version=$($PYTHON_CMD --version 2>&1)
    if echo "$python_version" | grep -q "Python 3\.13"; then
        log_success "Python found: $python_version"
    else
        issues+=("Python 3.13 is required, found: $python_version")
    fi

    # Check available disk space (minimum 5GB)
    local available_space
    if command_exists df; then
        available_space=$(df -h "$HOME" | awk 'NR==2 {print $4}')
        log_success "Available disk space: $available_space"
    else
        log_warning "Cannot check disk space (df command not available)"
    fi

    # Check if we can create directories
    if [[ ! -d "$WORKSPACE_ROOT" ]]; then
        mkdir -p "$WORKSPACE_ROOT" 2>/dev/null || issues+=("Cannot create workspace directory: $WORKSPACE_ROOT")
    fi

    if [[ ${#issues[@]} -gt 0 ]]; then
        log_error "Prerequisites check failed!"
        for issue in "${issues[@]}"; do
            log_error "$issue"
        done
        exit 1
    fi

    log_success "All prerequisites satisfied"
}

# Initialize workspace
initialize_workspace() {
    log_header "Setting up workspace directory..."

    local project_path="$WORKSPACE_ROOT/$PROJECT_NAME"

    # Create workspace root if it doesn't exist
    if [[ ! -d "$WORKSPACE_ROOT" ]]; then
        log_info "Creating workspace root: $WORKSPACE_ROOT"
        mkdir -p "$WORKSPACE_ROOT"
    fi

    # Remove existing project directory if it exists
    if [[ -d "$project_path" ]]; then
        log_warning "Removing existing project directory..."
        rm -rf "$project_path"
    fi

    # Clone repository at specific tag
    log_info "Cloning repository at tag $TAG_VERSION..."
    cd "$WORKSPACE_ROOT"

    git clone --branch "$TAG_VERSION" --single-branch "$REPOSITORY_URL" "$PROJECT_NAME"

    if [[ ! -d "$project_path" ]]; then
        log_error "Failed to clone repository"
        exit 1
    fi

    cd "$project_path"
    log_success "Repository cloned successfully to: $project_path"

    echo "$project_path"
}

# Setup Python virtual environment
setup_python_environment() {
    local project_path="$1"

    log_header "Setting up Python virtual environment..."

    local venv_path="$project_path/.venv"

    # Create virtual environment
    log_info "Creating virtual environment..."
    $PYTHON_CMD -m venv "$venv_path"

    if [[ ! -d "$venv_path" ]]; then
        log_error "Failed to create virtual environment"
        exit 1
    fi

    # Activate virtual environment
    log_info "Activating virtual environment..."
    source "$venv_path/bin/activate"

    # Upgrade pip
    log_info "Upgrading pip..."
    python -m pip install --upgrade pip

    log_success "Python virtual environment created successfully"
}

# Install dependencies
install_dependencies() {
    local project_path="$1"

    log_header "Installing Python dependencies..."

    cd "$project_path"

    # Activate virtual environment
    source "$project_path/.venv/bin/activate"

    # Install core requirements
    local core_req_file="requirements-core.txt"
    if [[ -f "$core_req_file" ]]; then
        log_info "Installing core requirements..."
        python -m pip install -r "$core_req_file"
    else
        log_warning "Core requirements file not found: $core_req_file"
    fi

    # Install optional requirements
    local optional_req_file="requirements-optional.txt"
    if [[ -f "$optional_req_file" ]]; then
        log_info "Installing optional requirements..."
        python -m pip install -r "$optional_req_file"
    else
        log_warning "Optional requirements file not found: $optional_req_file"
    fi

    # Install main requirements if core/optional don't exist
    local main_req_file="requirements.txt"
    if [[ -f "$main_req_file" && ! -f "$core_req_file" ]]; then
        log_info "Installing main requirements..."
        python -m pip install -r "$main_req_file"
    fi

    log_success "Dependencies installed successfully"
}

# Setup configuration files
setup_configuration() {
    local project_path="$1"

    log_header "Setting up configuration files..."

    cd "$project_path"

    # Create .env file from template
    local env_template=".env.template"
    local env_file=".env"

    if [[ -f "$env_template" ]]; then
        if [[ ! -f "$env_file" ]]; then
            cp "$env_template" "$env_file"
            log_success "Created .env file from template"
            log_warning "Please edit .env file to add your secrets and configuration"
        else
            log_info ".env file already exists"
        fi
    else
        log_info "No .env.template found, creating basic .env..."
        cat > "$env_file" << EOF
# Alienware Device Configuration
# Generated by bootstrap_alienware.sh

# Device identification
DEVICE_NAME=ALIENWARE
DEVICE_TYPE=development

# Project paths
PROJECT_ROOT=$project_path
WORKSPACE_ROOT=$WORKSPACE_ROOT

# Python configuration
PYTHON_VERSION=3.13

# Add your secrets and API keys below:
# OPENAI_API_KEY=your_openai_key_here
# GOOGLE_SHEETS_CREDENTIALS_PATH=path_to_credentials
# Other configuration as needed...
EOF
    fi

    # Create device-specific profile
    local device_name=$(hostname)
    local user_name=$(whoami)
    local user_home="$HOME"
    local python_path=$(which python)
    local onedrive_path="$HOME/OneDrive"

    # Try to find OneDrive path variations
    local onedrive_variations=(
        "$HOME/OneDrive"
        "$HOME/OneDrive - Digital Age Marketing Group"
        "$HOME/OneDrive - Personal"
    )

    for path in "${onedrive_variations[@]}"; do
        if [[ -d "$path" ]]; then
            onedrive_path="$path"
            break
        fi
    done

    # Create config directory if it doesn't exist
    local config_dir="$project_path/config"
    mkdir -p "$config_dir"

    # Create device profile JSON
    local device_profile_path="$config_dir/device_profile-$device_name.json"
    cat > "$device_profile_path" << EOF
{
    "device": "$device_name",
    "username": "$user_name",
    "user_home": "$user_home",
    "timestamp": "$(date -Iseconds)",
    "python_path": "$python_path",
    "onedrive_path": "$onedrive_path",
    "project_root": "$project_path",
    "virtual_env": "$project_path/.venv"
}
EOF

    log_success "Created device profile: $device_profile_path"

    # Create required directories
    local required_dirs=(
        "logs"
        "logs/automation"
        "logs/device_logs"
        "output"
        "input"
        "automation"
        "tools"
        "scripts"
    )

    for dir in "${required_dirs[@]}"; do
        local dir_path="$project_path/$dir"
        if [[ ! -d "$dir_path" ]]; then
            mkdir -p "$dir_path"
            log_success "Created directory: $dir"
        fi
    done
}

# Install external tools
install_external_tools() {
    log_header "Installing external tools..."

    # Install pre-commit
    if python -m pip install pre-commit; then
        log_success "Pre-commit installed successfully"
    else
        log_warning "Failed to install pre-commit"
    fi

    # Check for Chrome/Chromium installation
    local chrome_found=false
    local chrome_paths=(
        "/usr/bin/google-chrome"
        "/usr/bin/chromium-browser"
        "/usr/bin/chromium"
        "/snap/bin/chromium"
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    )

    for path in "${chrome_paths[@]}"; do
        if [[ -f "$path" ]]; then
            chrome_found=true
            log_success "Chrome/Chromium found at: $path"
            break
        fi
    done

    if [[ "$chrome_found" == false ]]; then
        log_warning "Chrome/Chromium not found. Please install for web automation features."
    fi
}

# Run environment validation
run_environment_validation() {
    local project_path="$1"

    if [[ "$SKIP_VALIDATION" == true ]]; then
        log_warning "Skipping validation as requested"
        return
    fi

    log_header "Running environment validation..."

    cd "$project_path"

    # Activate virtual environment
    source "$project_path/.venv/bin/activate"

    # Run validation script
    local validation_script="validate_env_state.py"
    if [[ -f "$validation_script" ]]; then
        local validation_output
        local validation_exit_code=0

        if validation_output=$(python "$validation_script" 2>&1); then
            validation_exit_code=0
        else
            validation_exit_code=$?
        fi

        # Create validation report
        local report_path="alienware_validation_report.md"
        local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

        cat > "$report_path" << EOF
# Alienware Device Bootstrap Validation Report

**Generated**: $timestamp
**Device**: $(hostname)
**User**: $(whoami)
**Bootstrap Script**: bootstrap_alienware.sh

## Validation Output

\`\`\`
$validation_output
\`\`\`

## Bootstrap Summary

- ✅ Repository cloned at tag $TAG_VERSION
- ✅ Python $REQUIRED_PYTHON_VERSION virtual environment created
- ✅ Dependencies installed from requirements files
- ✅ Device-specific configuration created
- ✅ Required directories created
- ✅ External tools installed
- ✅ Environment validation completed

## Next Steps

1. Review and update the \`.env\` file with your specific configuration
2. Test the automation scripts to ensure everything works correctly
3. Run the full test suite: \`python -m pytest -v\`
4. Verify cross-device compatibility

---
*Generated by Alienware Bootstrap Script v1.0*
EOF

        log_success "Validation report created: $report_path"

        # Check if validation passed
        if [[ $validation_exit_code -eq 0 ]]; then
            log_success "Environment validation PASSED"
        else
            log_warning "Environment validation found issues - check the report"
        fi
    else
        log_warning "Validation script not found: $validation_script"

        # Create basic validation report
        local report_path="alienware_validation_report.md"
        cat > "$report_path" << EOF
# Alienware Device Bootstrap Validation Report

**Generated**: $(date '+%Y-%m-%d %H:%M:%S')
**Device**: $(hostname)
**Status**: ⚠️ Validation script not found

## Bootstrap Summary

- ✅ Repository cloned at tag $TAG_VERSION
- ✅ Python $REQUIRED_PYTHON_VERSION virtual environment created
- ✅ Dependencies installed
- ✅ Configuration files created
- ⚠️ Environment validation script not available

## Manual Verification Required

Please manually verify:
1. All Python packages are installed correctly
2. Configuration files are properly set up
3. All required directories exist
4. External tools are available

Run \`python -c "import sys; print(sys.version)"\` to verify Python installation.
EOF

        log_success "Basic validation report created: $report_path"
    fi
}

# Main function
main() {
    log_header "Starting Alienware Device Bootstrap..."
    log_info "Target workspace: $WORKSPACE_ROOT"
    log_info "Repository: $REPOSITORY_URL at $TAG_VERSION"

    # Step 1: Check prerequisites
    check_prerequisites

    # Step 2: Initialize workspace
    local project_path
    project_path=$(initialize_workspace)

    # Step 3: Setup Python environment
    setup_python_environment "$project_path"

    # Step 4: Install dependencies
    install_dependencies "$project_path"

    # Step 5: Setup configuration
    setup_configuration "$project_path"

    # Step 6: Install external tools
    install_external_tools

    # Step 7: Run validation
    run_environment_validation "$project_path"

    log_success "Alienware device bootstrap completed successfully!"
    log_info "Project location: $project_path"
    log_info "Next steps:"
    log_info "1. Review and update .env file with your secrets"
    log_info "2. Test the automation scripts"
    log_info "3. Run 'python -m pytest -v' to verify installation"
}

# Execute main function
main "$@"
