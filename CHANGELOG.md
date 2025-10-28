# Changelog

## [Unreleased]

### Added
- **Adapters Pass-1**: Thin adapters to preserved utilities (`normalize`, `validate_record`, `load_validators`) with 500ms timeout and safe fallbacks.
- **Safe Mode**: `BDR_SAFE_MODE` (default `1`) enables no-op fallbacks; set to `0` to attempt real imports.
- **Configurable Timeout**: `BDR_ADAPTER_TIMEOUT_MS` (default `500`) controls per-call timeout when safe mode is disabled.

## [v0.1.0] - 2025-10-27

### Added
- Initial stable release with 6 required CI checks (audit, fast-tests ubuntu/windows, workflow-guard, ps-lint ubuntu/windows)
- CLI demo with ingest/normalize/validate/score/report commands
- Security quieting and locked dependencies

## [v2.0-cross-device] - 2025-08-06 - Phase 2 Cross-Device Parity Close-Out (ASUS)

### Added
- **Phase 2 Cross-Device Parity Completion**: Applied final updates on ASUS device for consistency with Alienware
- **Line Length Standardization**: Updated Black and flake8 configurations for 79-character line limit
- **Pre-commit Configuration Updates**: Enhanced code quality tools with standardized line length enforcement
- **Final Phase 2 Validation**: Comprehensive testing and security scanning completion
- **Official Version Tagging**: Repository tagged as v2.0-cross-device for Phase 2 completion

### Changed
- **Code Formatting Standards**: Applied Black formatting with 79-character line limit across all Python files
- **Pre-commit Hooks**: Updated flake8 and Black configurations for consistent line length enforcement
- **Documentation Updates**: Finalized Phase 3 roadmap and cross-device implementation guides

### Technical Achievements
- **Cross-Device Parity**: Successfully replicated all Phase 2 changes on ASUS device (ACE)
- **Code Quality Standardization**: Enforced consistent formatting and linting standards
- **Security Validation**: Completed comprehensive secrets scanning and security verification
- **Test Coverage**: Maintained high test coverage across src/ and universal_recon/ modules

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
=======

## [v3.0] — TBD

### Planned

- Advanced automation & scalability features
- Enterprise SLA monitoring and alerting
- Multi-region deployment capabilities
- Enhanced plugin architecture

## [v2.0-cross-device] - 2025-08-05

### Added

- **Cross-Device Parity Completion**: Finalized branch cleanup, CI consolidation, and audit fixes
- **ACE Device Integration**: Successfully replicated Phase 2 close-out steps on ASUS device
- **Branch Management**: Cleaned up stale feature branches (ali-audit-fixes, improve-nightly-checks, fix-whitespace-ali)

## [v2.0-cross-device] - 2025-07-30

### Added

- **🎯 Alienware Bootstrap Bundle** - Complete deployment package for cross-device parity
  - **Bootstrap Bundle**: `alienware_bootstrap_bundle.zip` (27.4KB, 8 files) for immediate deployment
  - **PowerShell Script**: `bootstrap_alienware.ps1` (529 lines) for Windows deployment
  - **Bash Script**: `bootstrap_alienware.sh` (523 lines) for Linux/macOS deployment
  - **Environment Templates**: `.env.template` with Alienware-specific configuration
  - **Device Profile**: `config/device_profile-Alienware.json` for device-specific settings
  - **Validation Tools**: `validate_env_state.py` and `validate_alienware_bootstrap.py`
  - **Automation Playbook**: `alienware_playbook.ps1` (675 lines) for end-to-end setup
  - **Access Guide**: `ALI_BOOTSTRAP_ACCESS_GUIDE.md` with deployment instructions

- **🤝 Cross-Device Parity Achievements**
  - **95%+ Environment Parity**: Verified compatibility between ASUS and Alienware platforms
  - **Unified PowerShell Scripts**: Combined Unicode fixes (ACE) with 64-bit handling (ALI)
  - **Cross-Platform Validation**: Audit reports from both `audits/ace/` and `audits/ali/`
  - **Git LFS Support**: Proper handling of bootstrap bundle as deployment artifact
  - **Protected Branch Workflow**: Feature branch deployment to bypass main branch protection

### Fixed

- **Git Repository Access**: Resolved protected branch issues with feature branch workflow
- **Merge Conflicts**: Combined ALI and ACE enhancements in `.gitignore` and documentation
- **Bootstrap Bundle Tracking**: Added exception in `.gitignore` for critical deployment artifacts

### Changed

- **Release Tagging**: Updated to `v2.0-cross-device` reflecting complete cross-device integration
- **Documentation**: Enhanced PHASE3_ROADMAP.md with comprehensive cross-device notes
- **Branch Management**: Implemented proper feature branch workflow for protected main branch

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
