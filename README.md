# Universal Recon Tool (v4)

## Overview
The Universal Recon Tool is designed to automate reconnaissance for various bar directory websites, identifying elements like profile structures, pagination, and email obfuscation methods. The latest version integrates advanced features such as:

- Multi-step form handling
- Shadow DOM detection
- CAPTCHA mitigation
- AJAX-based content stabilization
- Intelligent session recovery & logging

## Installation
Ensure you have **Python 3.12+** installed, then run:
```sh
pip install -r requirements.txt
```

## Configuration
Update the `.env` file with your system paths and API credentials.

## Running the Tool
```sh
python src/universal_recon.py --url "https://examplebar.org"
```

## Features
- **Pagination Handling:** Detects and processes numeric, AJAX, and button-based paginations.
- **Profile Extraction:** Identifies key elements like names, emails, and bar numbers.
- **Error Logging:** Saves logs and screenshots for debugging failed runs.

## Contribution
Ensure you create a feature branch and submit a PR before merging into `main`.