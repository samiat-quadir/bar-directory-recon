# Changelog

## [2.1.0] - 2025-08-05 - Phase 2 Close-out (Alienware)

### Added
- **Consolidated Python dependencies**: Single `requirements.txt` with pinned versions for production
- **Development requirements**: Separate `requirements-dev.txt` for development tools
- **Architecture documentation**: Comprehensive `docs/architecture.md` explaining src/ vs universal_recon/ structure
- **Enhanced CI/CD pipeline**: Matrix-driven GitHub Actions workflow with multiple Python versions
- **Advanced pre-commit hooks**: Added black, isort, flake8, and mypy for code quality
- **Phase 3 roadmap**: Detailed planning document for production readiness and scalability

### Changed
- **Requirements management**: Moved from loose version ranges to pinned dependencies
- **Pre-commit configuration**: Enhanced with comprehensive code quality tools
- **GitHub workflows**: Consolidated multiple workflow files into single matrix-driven CI

### Removed
- **Legacy requirement files**: Deleted `requirements-core.txt`, `requirements-optional.txt`, `requirements-frozen.txt`
- **Redundant workflows**: Removed duplicate and device-specific GitHub Actions files
- **Unpinned dependencies**: Eliminated version range specifications in favor of exact pins

### Security
- **Secrets scanning**: Implemented comprehensive credential detection and removal
- **Environment variable migration**: Replaced hard-coded secrets with env-var references
- **Security verification**: Added automated security scanning to CI pipeline

### Infrastructure
- **Cross-device parity**: Achieved consistent development environment across Alienware and ASUS
- **Streamlined tooling**: Reduced tools/ directory to essential utilities with clear documentation
- **Quality assurance**: Implemented comprehensive testing and linting pipeline

## [Unreleased]

### Added

- **🏠 Realtor Directory Automation System** for automated lead extraction
  - **Plugin system integration**: New `realtor_directory_plugin.py` for scraping directories.apps.realtor.com
  - **Multiple execution modes**: Single run, interactive mode, and weekly scheduling
  - **CSV export functionality**: Structured output with name, email, phone, business name, and address
  - **Google Sheets integration**: Optional upload to Google Sheets with service account authentication
  - **Cross-platform compatibility**: Windows batch files, PowerShell scripts, and Python automation
  - **Comprehensive CLI interface**: Full argument support through main.py and dedicated automation script
  - **Windows Task Scheduler integration**: XML template for weekly automation setup
  - **Interactive configuration**: User-guided setup with custom search parameters
  - **Robust error handling**: Comprehensive logging and graceful failure management
  - **Selenium + BeautifulSoup**: Dual scraping approach for static and dynamic content
- **Enhanced plugin registry system**: JSON-based plugin configuration and loading
- **Automated dependency management**: Setup script for one-click installation and configuration
- **Comprehensive documentation**: Full README with usage examples and troubleshooting

### Technical Implementation

- **Chrome WebDriver automation**: Headless browser automation with webdriver-manager
- **Rate limiting and ethical scraping**: Built-in delays and respectful crawling practices
- **Type safety**: Full type annotations and mypy compliance
- **Virtual environment support**: Automated venv creation and dependency isolation
- **Cross-device synchronization**: Compatible with existing cross-device infrastructure
- **Extensible architecture**: Plugin system allows for additional directory sources

### Dependencies Added

- `schedule>=1.2.0` - Python job scheduling
- `gspread>=5.12.0` - Google Sheets API integration
- `google-auth>=2.23.0` - Google Cloud authentication

### Files Added

- `universal_recon/plugins/realtor_directory_plugin.py` - Core scraping logic
- `universal_recon/plugin_registry.json` - Plugin configuration registry
- `realtor_automation.py` - Main automation script with CLI interface
- `realtor_automation_scheduler.ps1` - PowerShell Task Scheduler integration
- `RunRealtorAutomation.bat` - Windows batch runner for easy execution
- `setup_realtor_automation.py` - Automated setup and dependency installation
- `README_REALTOR_AUTOMATION.md` - Comprehensive user documentation
- `outputs/` - Directory for CSV output files with documentation
- `logs/` - Directory for execution logs and monitoring

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 0.1.1 – Rotated credentials & hardened CI

### Security

- **Credential rotation**: Updated and secured API tokens and secrets
- **CI/CD hardening**: Enhanced GitHub Actions workflow security
- **Access control**: Improved repository security configurations

### Changed

- Updated PyPI publishing workflow for better security practices
- Enhanced authentication mechanisms

## 0.1.0 – Initial Preview

### Added

- **Core reconnaissance framework** for legal bar directory automation
- **Plugin system** with modular architecture:
  - Social link parser for LinkedIn, Twitter, Facebook, Instagram detection
  - ML labeler for intelligent content classification
  - Firm parser for law firm data extraction
  - Email and contact information extractors
- **Analytics suite**:
  - Risk overlay emitter for validation assessment
  - Plugin usage difference tracking
  - Validator drift detection and reporting
  - Template health flagging
  - Score visualization and heatmap generation
- **Infrastructure components**:
  - ChromeDriver automation support
  - Cross-device compatibility testing
  - Comprehensive test suite (33 tests passing)
  - Pre-commit hooks for code quality
- **Data validation and processing**:
  - Record normalization utilities
  - Schema validation system
  - Field mapping and domain linting
  - Score prediction and suppression tools
- **Documentation and tooling**:
  - Phase 29 development backlog tracking
  - Comprehensive README with setup instructions
  - MIT license
  - GitHub CI/CD workflows

### Technical Features

- Python 3.11+ compatibility
- BeautifulSoup4 for HTML parsing
- Selenium WebDriver integration
- YAML configuration support
- JSON output formatting
- Extensive error handling and logging

### Quality Assurance

- 100% test coverage for core functionality
- Type hints throughout codebase
- Pre-commit hooks for linting and formatting
- Cross-platform Windows/Linux compatibility
- Automated CI/CD pipeline

This initial release provides a solid foundation for legal directory reconnaissance and automation tasks, with a focus on data extraction, validation, and analysis capabilities.
