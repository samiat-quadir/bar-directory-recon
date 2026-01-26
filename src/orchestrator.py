#!/usr/bin/env python3
"""
Unified Scraper Orchestrator
Main controller that coordinates all scraping operations using the modular framework.

Integrity Enhancements (v2.0):
- Validation threshold enforcement
- Empty result failure detection
- Output collision prevention
- Deduplication transparency
- UTC timezone support
"""

import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pandas as pd

from config_loader import ConfigLoader
from data_extractor import DataExtractor
from logger import create_logger
from pagination_manager import PaginationManager
from unified_schema import SchemaMapper

# Integrity policy imports (optional - graceful degradation)
try:
    from policies import ValidationPolicy, ExportPolicy, FailurePolicy, enforce_validation_threshold
    from reports import DeduplicationReport, ValidationSummary, deduplicate_with_tracking
    INTEGRITY_POLICIES_AVAILABLE = True
except ImportError:
    INTEGRITY_POLICIES_AVAILABLE = False
# webdriver_manager may be an external package or a local module in this repo.
# Import defensively: prefer local module if present to avoid 'is not a package' errors
try:
    from webdriver_manager import WebDriverManager  # type: ignore
except Exception:
    # Provide a lightweight stub so import-only tests don't fail when Selenium
    # and webdriver_manager are not installed in the CI environment.
    class WebDriverManager:  # type: ignore
        def __init__(self, cfg=None):
            self.cfg = cfg
            self.driver = None

        def navigate_to(self, url: str) -> bool:  # pragma: no cover - stub
            return True

        def quit(self):
            return

# Google Sheets API scopes
GOOGLE_SHEETS_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.readonly",
]


class ScrapingOrchestrator:
    """Main orchestrator for unified scraping operations."""

    def __init__(
        self, 
        config_path: Union[str, Path],
        min_validation_score: float = 0.0,
        allow_empty: bool = True,
        export_rejected: bool = False,
        collision_strategy: str = 'uuid'
    ):
        """
        Initialize the scraping orchestrator.
        
        Args:
            config_path: Path to configuration file
            min_validation_score: Minimum score for record acceptance (0-100, default 0 = no filtering)
            allow_empty: Allow 0 URLs or records without raising error (default True = legacy behavior)
            export_rejected: Export low-score records to separate file (default False)
            collision_strategy: File collision prevention ('uuid', 'millisecond', 'increment')
        """
        self.config_loader = ConfigLoader()
        self.config = self.config_loader.load_config(config_path)
        # Load integrity config if present (with CLI arg override)
        integrity_cfg = self.config.integrity or {}
        integrity_enabled = integrity_cfg.get('enable', False)
        
        # Use config values if integrity.enable=true, otherwise use CLI args (with backward-compatible defaults)
        if integrity_enabled:
            min_validation_score = integrity_cfg.get('min_validation_score', 0.0)
            allow_empty = integrity_cfg.get('allow_empty', True)
            export_rejected = integrity_cfg.get('export_rejected', False)
            collision_strategy = integrity_cfg.get('collision_strategy', 'uuid')
        # else: use the function parameters (already set to backward-compatible defaults)


        # Initialize logger (use UTC timestamps if policies available)
        self.logger = create_logger(
            name=f"scraper_{self.config.name}",
            log_level=self.config.options.get("log_level", "INFO"),
        )

        # Initialize managers (will be created when needed)
        self.driver_manager: Optional[WebDriverManager] = None
        self.pagination_manager: Optional[PaginationManager] = None
        self.data_extractor: Optional[DataExtractor] = None

        # Results storage
        self.extracted_data: List[Dict[str, Any]] = []
        self.processed_urls: List[str] = []
        self.failed_urls: List[str] = []
        
        # Integrity policies (if available)
        if INTEGRITY_POLICIES_AVAILABLE:
            self.validation_policy = ValidationPolicy(
                min_score=min_validation_score,
                export_rejected=export_rejected
            )
            self.export_policy = ExportPolicy(collision_strategy=collision_strategy)
            self.failure_policy = FailurePolicy(
                allow_empty_urls=allow_empty,
                allow_empty_records=allow_empty
            )
            self.dedup_report = DeduplicationReport()
            self.validation_summary = ValidationSummary()
        else:
            self.logger.warning(
                "Integrity policies not available. "
                "Install policies package for enhanced data quality controls."
            )
            self.validation_policy = None
            self.export_policy = None
            self.failure_policy = None
            self.dedup_report = None
            self.validation_summary = None

        self.logger.log_config_loaded(str(config_path), self.config.name)

    def initialize_managers(self) -> None:
        """Initialize all manager instances."""
        try:
            # WebDriver configuration
            driver_config = {
                "headless": self.config.options.get("headless", True),
                "timeout": self.config.options.get("timeout", 30),
                "user_agent": self.config.options.get(
                    "user_agent",
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                ),
                "disable_js": self.config.options.get("disable_js", False),
                "viewport": self.config.options.get(
                    "viewport", {"width": 1920, "height": 1080}
                ),
            }

            self.driver_manager = WebDriverManager(driver_config)

            # Pagination configuration
            pagination_config = {
                "max_pages": self.config.pagination.get("max_pages", 10),
                "page_delay": self.config.pagination.get("delay", 2.0),
                "pagination_selectors": {
                    "next_button": self._ensure_list(
                        self.config.pagination.get("next_button", [])
                    ),
                    "load_more": self._ensure_list(
                        self.config.pagination.get("load_more", [])
                    ),
                    "page_numbers": self._ensure_list(
                        self.config.pagination.get("page_numbers", [])
                    ),
                },
            }

            self.pagination_manager = PaginationManager(
                self.driver_manager, pagination_config
            )

            # Data extraction configuration
            extraction_config = {
                "extraction_rules": {
                    "listing_container": self.config.listing_phase.get(
                        "list_selector", "body"
                    ),
                    "fields": self.config.data_extraction.get("selectors", {}),
                    "detail_url_selectors": self._ensure_list(
                        self.config.listing_phase.get("link_selector", [])
                    ),
                },
                "required_fields": self.config.data_extraction.get(
                    "required_fields", []
                ),
                "base_url": self.config.base_url,
                "current_url": "",
                "industry": self.config.name,
                "source_name": self.config.name,
            }

            self.data_extractor = DataExtractor(extraction_config)

            self.logger.info("All managers initialized successfully")

        except Exception as e:
            self.logger.error("Failed to initialize managers", exception=e)
            raise

    def _ensure_list(self, value: Any) -> List[str]:
        """Ensure value is a list of strings."""
        if isinstance(value, str):
            return [value]
        elif isinstance(value, list):
            return [str(item) for item in value]
        else:
            return []

    def run_listing_phase(self) -> List[str]:
        """Execute the listing phase to collect URLs."""
        self.logger.info("Starting listing phase")

        if not self.config.listing_phase.get("enabled", True):
            self.logger.info("Listing phase disabled, using base URL only")
            return [self.config.base_url]

        try:
            start_url = self.config.listing_phase.get("start_url", self.config.base_url)
            self.data_extractor.config["current_url"] = start_url

            # Navigate to start URL
            if not self.driver_manager.navigate_to(start_url):
                self.logger.error(f"Failed to navigate to start URL: {start_url}")
                return []

            all_urls = []

            # Process all pages with pagination
            for page_num in self.pagination_manager.paginate_all_pages():
                self.logger.log_pagination(page_num)

                # Extract URLs from current page
                page_urls = self.data_extractor.extract_listing_urls(
                    self.driver_manager
                )
                all_urls.extend(page_urls)

                self.logger.info(f"Page {page_num}: Found {len(page_urls)} URLs")

                # Add delay between pages
                delay = self.config.listing_phase.get("delay", 2.0)
                if delay > 0:
                    time.sleep(delay)

            # Remove duplicates with tracking (if policies available)
            if INTEGRITY_POLICIES_AVAILABLE and self.dedup_report:
                unique_urls = deduplicate_with_tracking(
                    all_urls, 
                    self.dedup_report, 
                    category='urls'
                )
                # Log deduplication summary
                total_count = len(all_urls)
                unique_count = len(unique_urls)
                duplicates_removed = total_count - unique_count
                if duplicates_removed > 0:
                    self.logger.info(
                        f"Deduplication: {total_count} total URLs → "
                        f"{unique_count} unique URLs ({duplicates_removed} duplicates removed)"
                    )
            else:
                # Preserve existing behavior when policies unavailable
                unique_urls = list(dict.fromkeys(all_urls))

            # Validate non-empty results (if policies available)
            if INTEGRITY_POLICIES_AVAILABLE and self.failure_policy:
                self.failure_policy.validate_url_extraction(unique_urls)

            self.logger.log_extraction_phase("listing", start_url, success=True)
            self.logger.info(
                f"Listing phase completed: {len(unique_urls)} unique URLs found"
            )

            return unique_urls

        except Exception as e:
            self.logger.error("Listing phase failed", exception=e)
            self.logger.log_extraction_phase("listing", start_url, success=False)
            return []

    def run_detail_phase(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Execute the detail phase to extract data from URLs."""
        self.logger.info(f"Starting detail phase with {len(urls)} URLs")

        if not self.config.detail_phase.get("enabled", True):
            self.logger.info("Detail phase disabled, extracting from listing pages")
            return self.extract_from_current_page()

        all_data = []

        for i, url in enumerate(urls, 1):
            try:
                self.logger.info(f"Processing URL {i}/{len(urls)}: {url}")
                self.data_extractor.config["current_url"] = url

                # Navigate to detail page
                if not self.driver_manager.navigate_to(url):
                    self.logger.warning(f"Failed to navigate to: {url}")
                    self.failed_urls.append(url)
                    continue

                # Extract data from current page
                page_data = self.data_extractor.extract_from_page(self.driver_manager)

                if page_data:
                    all_data.extend(page_data)
                    self.logger.log_page_processed(
                        url, success=True, records=len(page_data)
                    )

                    for record in page_data:
                        self.logger.log_record_extracted(record, url)
                else:
                    self.logger.log_page_processed(url, success=False)

                self.processed_urls.append(url)

                # Add delay between requests
                delay = self.config.detail_phase.get("delay", 1.0)
                if delay > 0:
                    time.sleep(delay)

            except Exception as e:
                self.logger.error(f"Failed to process URL {url}", exception=e)
                self.failed_urls.append(url)
                continue

        self.logger.log_extraction_phase("detail", f"{len(urls)} URLs", success=True)
        self.logger.info(f"Detail phase completed: {len(all_data)} records extracted")

        # Validate non-empty results (if policies available)
        if INTEGRITY_POLICIES_AVAILABLE and self.failure_policy:
            self.failure_policy.validate_record_extraction(all_data)

        return all_data

    def extract_from_current_page(self) -> List[Dict[str, Any]]:
        """Extract data from current page (single-phase scraping)."""
        try:
            return self.data_extractor.extract_from_page(self.driver_manager)
        except Exception as e:
            self.logger.error("Failed to extract from current page", exception=e)
            return []

    def run_scraping(self) -> Dict[str, Any]:
        """Run the complete scraping process."""
        start_time = datetime.now(timezone.utc)
        self.logger.info(f"Starting scraping session: {self.config.name}")

        try:
            # Initialize all managers
            self.initialize_managers()

            # Determine scraping strategy
            if self.config.listing_phase.get("enabled", True):
                # Two-phase scraping: listing -> detail
                urls = self.run_listing_phase()

                if not urls:
                    self.logger.warning("No URLs found in listing phase")
                    return self._create_result_summary(start_time, success=False)

                # Extract data from detail pages
                self.extracted_data = self.run_detail_phase(urls)
            else:
                # Single-phase scraping: extract from start page
                start_url = self.config.base_url
                self.data_extractor.config["current_url"] = start_url

                if not self.driver_manager.navigate_to(start_url):
                    self.logger.error(f"Failed to navigate to: {start_url}")
                    return self._create_result_summary(start_time, success=False)

                self.extracted_data = self.extract_from_current_page()

            # Clean and validate data
            if self.extracted_data:
                self.extracted_data = self.data_extractor.clean_extracted_data(
                    self.extracted_data
                )
                self.extracted_data = self.data_extractor.validate_and_enrich_data(
                    self.extracted_data
                )

            # Save results
            result_summary = self._save_results(start_time)

            self.logger.info(
                f"Scraping completed successfully: {len(self.extracted_data)} records"
            )
            return result_summary

        except Exception as e:
            self.logger.error("Scraping session failed", exception=e)
            return self._create_result_summary(start_time, success=False)

        finally:
            # Cleanup
            if self.driver_manager:
                self.driver_manager.quit()

            # Close logger
            self.logger.close()

    def _save_results(self, start_time: datetime) -> Dict[str, Any]:
        """Save results to configured outputs using unified schema."""
        try:
            output_files = []

            if not self.extracted_data:
                self.logger.warning("No data to save")
                return self._create_result_summary(start_time, success=True)

            # Initialize schema mapper
            schema_mapper = SchemaMapper()

            # Determine source type from config
            source_type = self.config.name.lower()
            if "lawyer" in source_type or "attorney" in source_type:
                source_type = "lawyers"
            elif "realtor" in source_type or "real" in source_type:
                source_type = "realtors"
            elif "contractor" in source_type:
                source_type = "contractors"
            else:
                source_type = "standard"

            # Apply unified schema mapping
            mapped_data = schema_mapper.map_data_to_unified_schema(
                self.extracted_data,
                source_type=source_type,
                source_name=self.config.name,
            )

            # Apply validation threshold (if policies available)
            accepted_data = mapped_data
            rejected_data = []
            
            if INTEGRITY_POLICIES_AVAILABLE and self.validation_policy:
                accepted_data, rejected_data = enforce_validation_threshold(
                    mapped_data,
                    self.validation_policy,
                    self.validation_summary
                )
                
                # Log validation results
                total_count = len(mapped_data)
                accepted_count = len(accepted_data)
                rejected_count = len(rejected_data)
                
                if rejected_count > 0:
                    self.logger.warning(
                        f"Validation threshold enforcement: {total_count} total records → "
                        f"{accepted_count} accepted, {rejected_count} rejected "
                        f"(min_score={self.validation_policy.min_score})"
                    )

            # Create DataFrame with unified schema column order
            df = schema_mapper.create_export_dataframe(
                accepted_data, export_type="standard"
            )

            # Generate output filename with collision prevention (if policies available)
            if INTEGRITY_POLICIES_AVAILABLE and self.export_policy:
                base_filename = self.export_policy.generate_safe_filename(
                    self.config.output.get("filename", self.config.name)
                )
            else:
                # Preserve existing behavior when policies unavailable
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                base_filename = self.config.output.get(
                    "filename", f"{self.config.name}_{timestamp}"
                )

            # Remove extension if present
            if "." in base_filename:
                base_filename = base_filename.rsplit(".", 1)[0]

            # Create output directory
            output_dir = Path("output") / self.config.name
            output_dir.mkdir(parents=True, exist_ok=True)

            # Save CSV (always) - using unified schema order
            csv_path = output_dir / f"{base_filename}.csv"
            df.to_csv(csv_path, index=False, encoding="utf-8")
            output_files.append(str(csv_path))
            self.logger.info(f"Data saved to CSV: {csv_path}")

            # Save JSON with unified schema
            json_path = output_dir / f"{base_filename}.json"
            df.to_json(json_path, orient="records", indent=2)
            output_files.append(str(json_path))
            self.logger.info(f"Data saved to JSON: {json_path}")

            # Save Excel with unified schema
            try:
                excel_path = output_dir / f"{base_filename}.xlsx"
                df.to_excel(excel_path, index=False)
                output_files.append(str(excel_path))
                self.logger.info(f"Data saved to Excel: {excel_path}")
            except Exception as e:
                self.logger.warning(f"Failed to save Excel file: {e}")

            # Export rejected records (if policies available and configured)
            if (INTEGRITY_POLICIES_AVAILABLE and self.validation_policy and 
                self.validation_policy.export_rejected and rejected_data):
                rejected_df = schema_mapper.create_export_dataframe(
                    rejected_data, export_type="standard"
                )
                rejected_csv = output_dir / f"{base_filename}_REJECTED.csv"
                rejected_df.to_csv(rejected_csv, index=False, encoding="utf-8")
                output_files.append(str(rejected_csv))
                self.logger.info(f"Rejected records saved to: {rejected_csv}")

            # Save validation summary (if policies available)
            if INTEGRITY_POLICIES_AVAILABLE and self.validation_summary:
                summary_path = output_dir / f"{base_filename}_validation_summary.json"
                self.validation_summary.save_report(summary_path)
                output_files.append(str(summary_path))
                self.logger.info(f"Validation summary saved to: {summary_path}")

            # Save deduplication report (if policies available)
            if INTEGRITY_POLICIES_AVAILABLE and self.dedup_report:
                dedup_path = output_dir / f"{base_filename}_deduplication_report.json"
                self.dedup_report.save_report(dedup_path)
                output_files.append(str(dedup_path))
                self.logger.info(f"Deduplication report saved to: {dedup_path}")

            # Google Sheets integration (if configured)
            google_config = self.config.output.get("google_sheets", {})
            if google_config.get("enabled", False):
                try:
                    self._save_to_google_sheets(df, google_config)
                except Exception as e:
                    self.logger.warning(f"Failed to save to Google Sheets: {e}")

            return self._create_result_summary(
                start_time, success=True, output_files=output_files
            )

        except Exception as e:
            self.logger.error("Failed to save results", exception=e)
            return self._create_result_summary(start_time, success=False)

    def _save_to_google_sheets(
        self, df: pd.DataFrame, google_config: Dict[str, Any]
    ) -> None:
        """Save data to Google Sheets using unified schema."""
        try:
            # Check if Google Sheets libraries are available
            try:
                from google.auth.transport.requests import Request
                from google.oauth2.credentials import Credentials
                from google_auth_oauthlib.flow import InstalledAppFlow
                from googleapiclient.discovery import build
            except ImportError:
                self.logger.error(
                    "Google Sheets libraries not installed. Install with: "
                    "pip install google-auth google-auth-oauthlib "
                    "google-auth-httplib2 google-api-python-client"
                )
                return

            # Get configuration
            credentials_path = google_config.get("credentials_path", "credentials.json")
            token_path = google_config.get("token_path", "token.json")
            sheet_id = google_config.get("sheet_id")
            worksheet_name = google_config.get("worksheet_name", "Scraped Data")

            if not sheet_id:
                self.logger.error("Google Sheets sheet_id not configured")
                return

            # Authentication
            creds = None
            if os.path.exists(token_path):
                creds = Credentials.from_authorized_user_file(
                    token_path, GOOGLE_SHEETS_SCOPES
                )

            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if not os.path.exists(credentials_path):
                        self.logger.error(
                            f"Google Sheets credentials file not found: {credentials_path}"
                        )
                        return

                    flow = InstalledAppFlow.from_client_secrets_file(
                        credentials_path, GOOGLE_SHEETS_SCOPES
                    )
                    creds = flow.run_local_server(port=0)

                # Save credentials for next run
                with open(token_path, "w") as token:
                    token.write(creds.to_json())

            # Build service
            service = build("sheets", "v4", credentials=creds)

            # Prepare data for upload
            values = []

            # Add headers
            values.append(list(df.columns))

            # Add data rows
            for _, row in df.iterrows():
                values.append([str(value) for value in row.values])

            # Upload to Google Sheets
            body = {"values": values}

            # Clear existing data and upload new data
            service.spreadsheets().values().clear(
                spreadsheetId=sheet_id, range=f"{worksheet_name}!A:Z"
            ).execute()

            result = (
                service.spreadsheets()
                .values()
                .update(
                    spreadsheetId=sheet_id,
                    range=f"{worksheet_name}!A1",
                    valueInputOption="RAW",
                    body=body,
                )
                .execute()
            )

            self.logger.info(
                f"Google Sheets updated: {result.get('updatedCells', 0)} cells updated"
            )

        except Exception as e:
            self.logger.error("Google Sheets save failed", exception=e)
            raise

    def _create_result_summary(
        self,
        start_time: datetime,
        success: bool,
        output_files: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Create a summary of the scraping results."""
        end_time = datetime.now(timezone.utc)
        runtime = end_time - start_time

        stats = self.logger.get_stats() if hasattr(self.logger, "get_stats") else {}

        return {
            "success": success,
            "session_name": self.config.name,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "runtime_seconds": runtime.total_seconds(),
            "runtime_formatted": str(runtime),
            "records_extracted": len(self.extracted_data),
            "urls_processed": len(self.processed_urls),
            "urls_failed": len(self.failed_urls),
            "output_files": output_files or [],
            "statistics": stats,
            "config_used": self.config.name,
        }

    def create_config_template(self, name: str, base_url: str, output_path: str) -> str:
        """Create a configuration template for a new directory."""
        try:
            config = self.config_loader.generate_sample_config(name, base_url)
            self.config_loader.save_config(config, output_path)

            self.logger.info(f"Configuration template created: {output_path}")
            return output_path

        except Exception as e:
            self.logger.error(f"Failed to create config template: {e}")
            raise

    @classmethod
    def quick_scrape(
        cls,
        name: str,
        base_url: str,
        list_selector: str = ".listing-item",
        max_pages: int = 5,
    ) -> Dict[str, Any]:
        """Quick scraping with minimal configuration."""
        try:
            # Create temporary config
            config_loader = ConfigLoader()
            config = config_loader.generate_sample_config(name, base_url)

            # Update with provided parameters
            config.listing_phase["list_selector"] = list_selector
            config.pagination["max_pages"] = max_pages

            # Save temporary config
            temp_config_path = Path("config") / f"temp_{name}.json"
            config_loader.save_config(config, temp_config_path)

            # Run scraping
            orchestrator = cls(temp_config_path)
            result = orchestrator.run_scraping()

            # Cleanup temp config
            if temp_config_path.exists():
                temp_config_path.unlink()

            return result

        except Exception as e:
            print(f"Quick scrape failed: {e}")
            return {"success": False, "error": str(e)}


# Convenience functions for direct usage
def scrape_directory(config_path: Union[str, Path]) -> Dict[str, Any]:
    """Scrape a directory using configuration file."""
    orchestrator = ScrapingOrchestrator(config_path)
    return orchestrator.run_scraping()


def quick_scrape(
    name: str, base_url: str, list_selector: str = ".listing-item", max_pages: int = 5
) -> Dict[str, Any]:
    """Quick scraping with minimal setup."""
    return ScrapingOrchestrator.quick_scrape(name, base_url, list_selector, max_pages)


def create_config(name: str, base_url: str, output_path: str) -> str:
    """Create a configuration template."""
    loader = ConfigLoader()
    config = loader.generate_sample_config(name, base_url)
    loader.save_config(config, output_path)
    return output_path
