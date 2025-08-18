# Development Container Setup Notes

## Overview

This devcontainer provides a complete development environment for the Bar Directory Recon project with:

- **Python 3.11** with all project dependencies
- **Google Chrome** with Selenium support (headless mode for containers)
- **Development tools**: pytest, black, flake8, mypy, pre-commit
- **Monitoring stack**: Prometheus, Grafana, PostgreSQL
- **VS Code extensions** for Python development

## Features

### Python Environment
- **Base**: Python 3.11 on Debian Bullseye
- **Package manager**: pip with latest setuptools and wheel
- **Dependencies**: All requirements from `requirements-dev.txt`
- **PYTHONPATH**: Configured for `src/` and `universal_recon/` modules

### Browser Automation
- **Chrome**: Latest stable version with container-safe flags
- **ChromeDriver**: Managed automatically via webdriver-manager
- **Selenium**: Configured for headless operation in containers

### Code Quality
- **Formatting**: Black (line length 88)
- **Import sorting**: isort (black-compatible profile)
- **Linting**: flake8 with reasonable ignores for black compatibility
- **Type checking**: mypy with flexible settings for development
- **Security**: bandit for security linting
- **Pre-commit**: Hooks for consistent code quality

### Testing
- **Framework**: pytest with coverage reporting
- **Coverage**: Targets `src/` and `universal_recon/` modules
- **Configuration**: Uses `pyproject.toml` settings
- **Threshold**: Currently set to 25% (incremental approach)

### Port Forwarding
- **3000**: Grafana dashboard
- **5432**: PostgreSQL database
- **8000**: Application metrics endpoint
- **8080**: cAdvisor container monitoring
- **9090**: Prometheus metrics server
- **9182**: Windows Exporter (for cross-device monitoring)

## Quick Commands

### Development
```bash
# Install dependencies
pip install -r requirements-dev.txt

# Run tests with coverage
pytest --cov=src --cov=universal_recon --cov-report=term-missing

# Format code
black .

# Check linting
flake8 .

# Type checking
mypy .

# Run all pre-commit hooks
pre-commit run --all-files
```

### Project Specific
```bash
# Run main application
python -m universal_recon.main

# Run setup verification
python setup_check.py

# Complete installation check
python complete_installation_check.py

# Verify dependencies
python verify_dependencies.py
```

### Docker Integration
```bash
# Start monitoring stack
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Environment Variables

The container sets up the following environment variables:

- `PYTHONPATH`: `/workspaces/bar-directory-recon/src:/workspaces/bar-directory-recon`
- `PYTHONDONTWRITEBYTECODE`: `1` (no .pyc files)
- `PYTHONUNBUFFERED`: `1` (real-time output)
- `CHROME_BIN`: `/usr/local/bin/chrome-no-sandbox` (container-safe Chrome)
- `PROJECT_NAME`: `bar-directory-recon`
- `ENVIRONMENT`: `development`
- `LOG_LEVEL`: `DEBUG`

## Chrome Configuration

Chrome is configured with container-safe options:
- `--no-sandbox`: Required for containerized environments
- `--disable-dev-shm-usage`: Prevents shared memory issues
- Available at `/usr/local/bin/chrome-no-sandbox`

## Troubleshooting

### Permission Issues
- The container runs as the `vscode` user
- Git safe directory is pre-configured
- Pre-commit hooks are installed automatically

### Browser Issues
- Use the container-safe Chrome binary for Selenium
- Headless mode is recommended for CI/testing
- Display server (DISPLAY=:99.0) is configured if needed

### Python Import Issues
- PYTHONPATH includes both `src/` and project root
- Install package in editable mode: `pip install -e .`
- Verify module structure matches imports

### Docker Issues
- Docker socket is mounted for docker-outside-of-docker
- Use `docker-compose` for multi-service development
- Check port forwarding for service access

## VS Code Integration

Pre-configured extensions provide:
- **Python**: Full language support with IntelliSense
- **Testing**: Integrated pytest runner
- **Formatting**: Automatic black formatting on save
- **Linting**: Real-time flake8 and mypy feedback
- **Git**: Enhanced Git integration with GitHub
- **Docker**: Container and compose management
- **Jupyter**: Notebook support for data analysis

## Security Considerations

- Container runs as non-root user (`vscode`)
- Chrome runs with security restrictions for containers
- Git credentials are handled securely through VS Code
- Secrets should use environment variables or `.env` files (gitignored)

## Performance

- **Resource requirements**: 2 CPUs, 4GB RAM, 8GB storage
- **Caching**: Workspace uses cached bind mounts
- **Optimization**: Dependencies are cached in container layers
- **Background services**: Monitoring stack runs separately via docker-compose
