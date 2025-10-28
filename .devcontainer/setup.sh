#!/bin/bash
# Development Container Setup Script
# This script is automatically executed when the devcontainer is created

set -e

echo "🚀 Setting up Bar Directory Recon development environment..."

# Display environment information
echo ""
echo "📋 Environment Information:"
echo "  Python: $(python --version)"
echo "  Node.js: $(node --version 2>/dev/null || echo 'Not installed')"
echo "  Git: $(git --version)"
echo "  Chrome: $(google-chrome --version 2>/dev/null || echo 'Not installed')"
echo "  Docker: $(docker --version 2>/dev/null || echo 'Not available')"
echo ""

# Upgrade pip and install requirements
echo "📦 Installing Python dependencies..."
python -m pip install --upgrade pip setuptools wheel

# Install development dependencies
if [ -f "requirements-dev.txt" ]; then
    echo "  Installing development requirements..."
    pip install -r requirements-dev.txt
else
    echo "  ⚠️  requirements-dev.txt not found, installing from requirements.txt"
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    else
        echo "  ❌ No requirements files found"
    fi
fi

# Install the package in editable mode
echo "  Installing package in development mode..."
pip install -e .

# Set up pre-commit hooks
echo "🔧 Setting up pre-commit hooks..."
if command -v pre-commit &> /dev/null; then
    pre-commit install --install-hooks
    echo "  ✅ Pre-commit hooks installed"
else
    echo "  ⚠️  pre-commit not available, skipping hooks setup"
fi

# Create necessary directories
echo "📁 Creating project directories..."
mkdir -p logs
mkdir -p archive
mkdir -p output
mkdir -p config
mkdir -p data
mkdir -p .pytest_cache
mkdir -p htmlcov

# Set proper permissions
chmod -R 755 scripts/ 2>/dev/null || true
chmod -R 755 tools/ 2>/dev/null || true

# Configure git safe directory
echo "🔐 Configuring git safe directory..."
git config --global --add safe.directory /workspaces/bar-directory-recon

# Run initial tests to verify setup
echo "🧪 Running initial verification..."
if command -v pytest &> /dev/null; then
    echo "  Running quick test suite..."
    python -m pytest --version
    echo "  Test framework ready ✅"
else
    echo "  ⚠️  pytest not available"
fi

# Verify key imports
echo "  Verifying key imports..."
python -c "
try:
    import src
    print('  ✅ src module importable')
except ImportError as e:
    print(f'  ⚠️  src module issue: {e}')

try:
    import universal_recon
    print('  ✅ universal_recon module importable')
except ImportError as e:
    print(f'  ⚠️  universal_recon module issue: {e}')

try:
    import selenium
    print('  ✅ Selenium available')
except ImportError:
    print('  ⚠️  Selenium not available')

try:
    import pandas
    print('  ✅ Pandas available')
except ImportError:
    print('  ⚠️  Pandas not available')
"

# Create welcome message
echo ""
echo "🎉 Development environment setup complete!"
echo ""
echo "📚 Quick Start Commands:"
echo "  Test coverage:     pytest --cov=src --cov=universal_recon --cov-report=term-missing"
echo "  Code formatting:   black ."
echo "  Linting:          flake8 ."
echo "  Type checking:     mypy ."
echo "  Pre-commit:       pre-commit run --all-files"
echo "  Run main:         python -m universal_recon.main"
echo ""
echo "🔧 Development Tools:"
echo "  VS Code extensions are pre-configured"
echo "  Ports forwarded: 3000 (Grafana), 9090 (Prometheus), 5432 (PostgreSQL)"
echo "  Chrome with --no-sandbox for containerized Selenium"
echo ""
echo "📖 Documentation:"
echo "  README.md - Project overview and setup"
echo "  DEPLOYMENT_GUIDE.md - Deployment instructions"
echo "  requirements-dev.txt - Development dependencies"
echo ""

# Display any additional setup notes
if [ -f ".devcontainer/SETUP_NOTES.md" ]; then
    echo "📝 Additional setup notes:"
    cat .devcontainer/SETUP_NOTES.md
fi

# Run setup validation
echo ""
echo "🔍 Running setup validation..."
if [ -f ".devcontainer/validate_setup.py" ]; then
    python .devcontainer/validate_setup.py
else
    echo "⚠️  Setup validation script not found"
fi

echo "✨ Happy coding! ✨"
