# Bar Directory Recon

[![CI Status](https://github.com/user/bar-directory-recon/actions/workflows/ci.yml/badge.svg)](https://github.com/user/bar-directory-recon/actions/workflows/ci.yml)
[![Dashboard](https://img.shields.io/badge/Dashboard-Live-brightgreen)](https://user.github.io/bar-directory-recon/)

## Project Overview

Bar Directory Recon is a comprehensive tool for gathering, analyzing, and organizing attorney directory data across multiple state bar associations.

## Features

- Automated data collection from state bar association websites
- Data validation and deduplication
- Exportable reports and visualizations
- Scheduled data refresh and monitoring

## Getting Started

1. Clone the repository
2. Create a `.env` file based on `.env.template`
3. Run `tools/sync_env.py` to set up your environment
4. Install dependencies: `pip install -r requirements.txt`
5. Run the application: `python src/universal_recon.py`

## Development

This project uses Python 3.12+ and follows best practices for code quality and testing.

### Environment Setup

Use the virtual environment `.venv311` for development:

#### Windows

tools/activate_venv.ps1

#### Linux/MacOS

source .venv311/bin/activate
pytest -v

```
# Windows
tools/activate_venv.ps1

# Linux/MacOS
source .venv311/bin/activate
```

### Run Tests

```
pytest -v
```

## Contributing

Contributions are welcome! Please follow the existing code style and add tests for new features.

## License

Proprietary - All rights reserved.
