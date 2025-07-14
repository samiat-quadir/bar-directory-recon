# Phase 5+ Final Touches - Legacy Cleanup Plan

## 1. Legacy Scripts and Modules to Archive/Remove

### ✅ Already Archived (in archive/ directory)

- Various legacy scripts and logs
- Old project audit reports

### 🔄 Need to Archive/Remove

**Legacy Batch Scripts (automation):**

- `weekly_automation.bat` - Replace with unified scheduler
- `RunRealtorAutomation.bat` - Replace with unified CLI
- `test_integration.bat` - Replace with test_framework.py
- Various device management scripts (cross-device functionality)

**Legacy Python Modules:**

- `usage_demo.py` - Replace with unified examples
- `google_sheets_integration.py` - Integrate into orchestrator
- `tools/realtor_directory_scraper.py` - Replaced by unified framework

**Legacy Universal Recon (keep core, archive redundant):**

- Keep: Core plugins that add value
- Archive: Duplicate functionality now in unified framework

## 2. Utility Functions to Migrate

### From google_sheets_integration.py

- Google Sheets authentication
- Data export formatting
- Duplicate detection logic

### From tools/realtor_directory_scraper.py

- Contact info extraction patterns
- Data validation logic

### From universal_recon/plugins/

- Firm parsing logic
- Social link extraction
- ML labeling functionality

## 3. Configuration Consolidation

### Current Configs

- `config/lawyer_directory.json` ✅ (unified format)
- `config/realtor_directory.json` ✅ (unified format)
- `universal_recon/plugin_registry.json` - Needs integration

### Hardcoded Values to Move

- Google credentials path in google_sheets_integration.py
- API keys and tokens scattered in scripts
- File paths in automation scripts

## 4. Automation Script Updates

### Scripts that need updating

- `Automated-GoogleSheets-Export.ps1` - Update to use unified CLI
- `weekly_automation.bat` - Replace with unified scheduler
- All cross-device management scripts

## 5. Schema Unification

### Current Data Schemas

**Unified Framework:**

- name, phone, email, address, company, url, scraped_at

**Google Sheets Integration:**

- name, company, email, phone, address, city, state, zip_code

**Legacy Tools:**

- Various inconsistent field names

**Target Unified Schema:**

- name, email, phone, company, address, city, state, zip_code, website, scraped_at, source, status

## Implementation Plan

1. ✅ Create notification module
2. ✅ Migrate Google Sheets functionality
3. ✅ Add configuration security audit
4. ✅ Add quiet/verbose logging toggle
5. ✅ Update automation scripts
6. ✅ Archive legacy files
7. ✅ Update documentation
