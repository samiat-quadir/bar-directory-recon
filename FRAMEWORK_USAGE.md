# Unified Scraping Framework - Usage Guide

## Overview

The unified scraping framework provides a modular, extensible architecture for scraping professional directories (lawyers, realtors, contractors, etc.). It consolidates legacy and universal scraping logic into a single, maintainable system.

## Core Components

### 1. WebDriverManager (`src/webdriver_manager.py`)

- Unified WebDriver setup and management
- Anti-detection features
- Browser automation utilities
- Context manager support

### 2. PaginationManager (`src/pagination_manager.py`)

- Handles various pagination patterns
- Supports: next buttons, load more, infinite scroll
- Configurable retry logic

### 3. DataExtractor (`src/data_extractor.py`)

- Configurable data extraction from HTML
- Contact information parsing
- Data validation and enrichment
- Multiple data formats support

### 4. ConfigLoader (`src/config_loader.py`)

- Loads and validates scraping configurations
- Supports JSON and YAML formats
- Schema validation
- Sample config generation

### 5. ScrapingLogger (`src/logger.py`)

- Structured logging and error tracking
- Session statistics
- Screenshot management
- Report generation

### 6. ScrapingOrchestrator (`src/orchestrator.py`)

- Main controller coordinating all components
- Supports single-phase and two-phase scraping
- Automated result saving
- Google Sheets integration (ready)

## Quick Start

### 1. Using the CLI

```bash
# Quick scrape (minimal setup)
python unified_scraper.py quick --name "lawyers" --url "https://lawyers.com" --selector ".lawyer-card"

# Create a new configuration
python unified_scraper.py config --name "realtor_directory" --url "https://realtors.com" --output "config/realtors.json"

# Run full scraping with configuration
python unified_scraper.py scrape --config "config/lawyer_directory.json" --max-pages 5

# List available configurations
python unified_scraper.py list --config-dir "config"

# Validate configuration
python unified_scraper.py validate --config "config/lawyer_directory.json"

# Test configuration (dry run)
python unified_scraper.py test --config "config/lawyer_directory.json"
```

### 2. Using the Framework Programmatically

```python
from src.orchestrator import ScrapingOrchestrator
from src.config_loader import ConfigLoader

# Load configuration
loader = ConfigLoader()
config = loader.load_config("config/lawyer_directory.json")

# Create orchestrator
orchestrator = ScrapingOrchestrator(config)

# Run scraping
results = orchestrator.run_scraping()

# Save results
orchestrator.save_results("output/lawyers_data.json")
```

## Configuration Format

### Sample Configuration (JSON)

```json
{
    "name": "lawyer_directory",
    "base_url": "https://lawyers.com",
    "scraping": {
        "strategy": "two_phase",
        "max_pages": 10,
        "delay_between_pages": 2,
        "list_page": {
            "url_pattern": "https://lawyers.com/page/{page}",
            "listing_selector": ".lawyer-card",
            "link_selector": "a.lawyer-link"
        },
        "detail_page": {
            "data_fields": {
                "name": ".lawyer-name",
                "phone": ".contact-phone",
                "email": ".contact-email",
                "address": ".address-full"
            }
        }
    },
    "pagination": {
        "type": "next_button",
        "next_selector": ".next-page",
        "max_retries": 3
    },
    "output": {
        "format": "json",
        "file_path": "output/lawyers_data.json",
        "google_sheets": {
            "enabled": false,
            "sheet_id": "",
            "worksheet_name": ""
        }
    }
}
```

## Framework Features

### ✅ Completed Features

- Modular architecture with clean separation of concerns
- Unified WebDriver management with anti-detection
- Flexible pagination handling
- Configurable data extraction
- Comprehensive logging and error tracking
- CLI interface for easy usage
- Configuration validation
- Sample configurations for lawyers and realtors

### 🔄 Ready for Integration

- Google Sheets integration (API ready)
- Multiple browser support (Chrome, Firefox, Edge)
- Data validation and enrichment
- Screenshot capture for debugging
- Session reporting

### 📋 Usage Examples

#### Scraping Lawyers Directory

```bash
python unified_scraper.py scrape --config "config/lawyer_directory.json" --max-pages 10
```

#### Creating Custom Configuration

```bash
python unified_scraper.py config --name "contractors" --url "https://contractors.com" --output "config/contractors.json"
```

#### Testing Configuration

```bash
python unified_scraper.py test --config "config/realtor_directory.json"
```

## Error Handling and Logging

The framework provides comprehensive error handling:

- All errors are logged with timestamps
- Screenshots are captured on failures
- Session statistics are tracked
- Detailed reports are generated

## Best Practices

1. **Always validate configurations** before running large scraping jobs
2. **Use test mode** to verify scraping logic on small datasets
3. **Monitor logs** for warnings and errors
4. **Respect website rate limits** by configuring appropriate delays
5. **Use headless mode** for production scraping
6. **Save screenshots** for debugging complex extraction issues

## Extending the Framework

### Adding New Pagination Types

Extend `PaginationManager` in `src/pagination_manager.py`

### Adding New Data Extractors

Extend `DataExtractor` in `src/data_extractor.py`

### Adding New Output Formats

Extend `ScrapingOrchestrator` in `src/orchestrator.py`

## Support

For questions or issues:

1. Check the logs in the `logs/` directory
2. Use test mode to debug configuration issues
3. Enable screenshots for visual debugging
4. Review the sample configurations in `config/`

## Current Status

The framework is ready for production use with:

- ✅ All core components implemented
- ✅ Type safety improvements completed
- ✅ Error handling and logging
- ✅ CLI interface
- ✅ Configuration validation
- ✅ Sample configurations

The next steps would be:

- End-to-end testing on real websites
- Google Sheets integration activation
- Additional sample configurations
- Performance optimization
- Documentation refinement
