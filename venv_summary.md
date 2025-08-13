# .venv Virtual Environment Structure Summary

## Main Directory Structure
```
.venv/
├── Include/           # Header files for C extensions
├── Lib/              # Python libraries and site-packages
├── Scripts/          # Executable scripts and Python interpreter
├── share/            # Shared data and man pages
├── pyvenv.cfg        # Virtual environment configuration
└── .gitignore        # Git ignore rules
```

## Key Installed Packages (from site-packages analysis):

### Web Development & APIs
- **fastapi** - Modern web framework
- **aiohttp** - Async HTTP client/server
- **uvicorn** - ASGI server
- **starlette** - Lightweight ASGI framework
- **httpx** - Modern HTTP client
- **requests** - HTTP library

### Data Processing & Analysis
- **pandas** - Data manipulation and analysis
- **numpy** - Numerical computing
- **openpyxl** - Excel file handling
- **PyPDF2** - PDF processing
- **pdfplumber** - PDF text extraction
- **tabula-py** - PDF table extraction

### Cloud & Azure Services
- **azure-core**, **azure-identity**, **azure-keyvault-secrets**
- **azure-storage-blob** - Azure cloud services
- **prefect** - Workflow orchestration

### Google APIs & Services
- **google-api-python-client** - Google APIs
- **gspread** - Google Sheets API
- **google-auth**, **google-auth-oauthlib** - Authentication

### Database & ORM
- **sqlalchemy** - SQL toolkit and ORM
- **alembic** - Database migration tool
- **asyncpg** - PostgreSQL async driver
- **aiosqlite** - Async SQLite

### Testing & Quality Assurance
- **pytest**, **pytest-cov** - Testing framework
- **black** - Code formatter
- **flake8** - Linting
- **mypy** - Type checking
- **bandit** - Security linting
- **pre-commit** - Git hooks

### Automation & Browser Control
- **selenium** - Web browser automation
- **playwright** - Modern browser automation
- **webdriver-manager** - WebDriver management

### Communication & Notifications
- **apprise** - Notification library
- **twilio** - SMS/voice services

### Utilities & Tools
- **schedule** - Job scheduling
- **tqdm** - Progress bars
- **colorama** - Cross-platform colored terminal text
- **click** - Command line interface creation
- **typer** - Modern CLI framework
- **rich** - Rich text and beautiful formatting

### File Processing
- **Pillow (PIL)** - Image processing
- **lxml** - XML/HTML processing
- **beautifulsoup4** - HTML/XML parsing
- **markdown** - Markdown processing

## Total Structure:
- **30,948+ files and directories**
- **Python 3.13.5** environment
- **Comprehensive development stack** for web development, data processing, automation, and cloud services

This virtual environment represents a sophisticated development setup with extensive capabilities for:
- Web application development
- Data analysis and processing
- Cloud service integration
- Browser automation
- API development and consumption
- Database operations
- Code quality assurance
