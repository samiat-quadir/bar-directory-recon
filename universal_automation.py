#!/usr/bin/env python3
"""
Universal Lead Generation Automation - Phase 4 Optimize Prime
Multi-industry lead scraping with advanced CRM integration
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

# Phase 4 imports
from lead_enrichment_plugin import LeadEnrichmentEngine

# Google Sheets integration (optional)
try:
    GOOGLE_SHEETS_AVAILABLE = True
except ImportError:
    GOOGLE_SHEETS_AVAILABLE = False

# Add project path for imports
script_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(script_dir))

# Configure logging to write to logs directory
logs_dir = script_dir / "logs"
logs_dir.mkdir(exist_ok=True)

# Set up file logging with timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = logs_dir / f"lead_automation_{timestamp}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(log_file), logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)
logger.info(f"Logging initialized. Log file: {log_file}")

# Available industries
AVAILABLE_INDUSTRIES = [
    "real_estate",
    "pool_contractors",
    "lawyers",
    "hvac_plumbers",
    "auto_dealers",
    "home_services",
    "professional_services",
    "design_services",
]


class UniversalLeadAutomation:
    """Multi-industry lead generation automation system."""

    def __init__(self):
        self.script_dir = script_dir
        self.plugin_registry_path = (
            self.script_dir / "universal_recon" / "plugin_registry.json"
        )
        self.outputs_dir = self.script_dir / "outputs"
        self.logs_dir = self.script_dir / "logs"
        self.plugins = self.load_plugin_registry()

        # Ensure directories exist
        self.outputs_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)

    def load_plugin_registry(self) -> List[Dict[str, Any]]:
        """Load the plugin registry."""
        try:
            with open(self.plugin_registry_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading plugin registry: {e}")
            return []

    def get_available_industries(self) -> List[str]:
        """Get list of available industries from plugin registry."""
        industries = []
        for plugin in self.plugins:
            if "industry" in plugin:
                industries.append(plugin["industry"])
        return sorted(list(set(industries)))

    def filter_plugins_by_industry(self, industry: str) -> List[Dict[str, Any]]:
        """Filter plugins by industry."""
        if industry == "all":
            return self.plugins

        filtered_plugins = []
        for plugin in self.plugins:
            if plugin.get("industry") == industry:
                filtered_plugins.append(plugin)

        return filtered_plugins

    def generate_tag(self, city: str, industry: str) -> str:
        """Generate a tag based on city and industry."""
        city_clean = (
            city.lower().replace(" ", "_").replace("-", "_") if city else "unknown"
        )
        industry_clean = industry.lower().replace(" ", "_")
        return f"{city_clean}_{industry_clean}"

    def create_output_directory(self, industry: str, city: str) -> Path:
        """Create organized output directory structure."""
        industry_dir = self.outputs_dir / industry
        city_dir = industry_dir / (
            city.lower().replace(" ", "_") if city else "unknown_city"
        )

        city_dir.mkdir(parents=True, exist_ok=True)
        return city_dir

    def run_plugin(
        self, plugin: Dict[str, Any], config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run a specific plugin."""
        try:
            # Import the plugin module
            module_path = plugin["module"]
            parts = module_path.split(".")

            # Dynamic import
            module = __import__(module_path, fromlist=[parts[-1]])
            plugin_function = getattr(module, plugin["function"])

            # Run the plugin
            logger.info(f"Running plugin: {plugin['site_name']}")
            result = plugin_function(config)

            # Add plugin metadata
            result["plugin_name"] = plugin["site_name"]
            result["industry"] = plugin.get("industry", "unknown")

            return result

        except Exception as e:
            logger.error(f"Error running plugin {plugin['site_name']}: {e}")
            return {
                "success": False,
                "error": str(e),
                "leads": [],
                "count": 0,
                "plugin_name": plugin["site_name"],
                "industry": plugin.get("industry", "unknown"),
            }

    def save_leads_to_csv(
        self,
        leads: List[Dict[str, Any]],
        industry: str,
        city: str,
        filename_prefix: str = "leads",
    ) -> Path:
        """Save leads to organized CSV structure."""

        if not leads:
            logger.warning("No leads to save")
            return None

        # Create output directory
        output_dir = self.create_output_directory(industry, city)

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{filename_prefix}_{timestamp}.csv"
        output_path = output_dir / filename

        # Save to CSV
        df = pd.DataFrame(leads)
        df.to_csv(output_path, index=False)

        logger.info(f"Saved {len(leads)} leads to: {output_path}")
        return output_path

    def setup_google_sheets(
        self, credentials_path: Optional[str] = None
    ) -> Optional[Any]:
        """Setup Google Sheets API client (optional)."""
        if not GOOGLE_SHEETS_AVAILABLE:
            logger.warning(
                "Google Sheets integration not available. "
                "Install google-api-python-client and google-auth packages."
            )
            return None

        if not credentials_path:
            credentials_path = str(
                self.script_dir / "config" / "google_service_account.json"
            )

        if not os.path.exists(credentials_path):
            logger.warning(
                f"Google Sheets credentials not found at: {credentials_path}"
            )
            return None

        try:
            from google.oauth2.service_account import Credentials
            from googleapiclient.discovery import build

            # Define the required scopes
            SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

            # Load credentials
            credentials = Credentials.from_service_account_file(
                credentials_path, scopes=SCOPES
            )

            # Build the service
            service = build("sheets", "v4", credentials=credentials)
            logger.info("Google Sheets API client initialized successfully")
            return service

        except Exception as e:
            logger.error(f"Error setting up Google Sheets: {e}")
            return None

    def upload_to_google_sheets(
        self,
        leads: List[Dict[str, Any]],
        sheet_id: str,
        sheet_name: Optional[str] = None,
    ) -> bool:
        """Upload leads to Google Sheets (optional functionality)."""

        if not GOOGLE_SHEETS_AVAILABLE:
            logger.warning("Google Sheets integration not available")
            return False

        service = self.setup_google_sheets()
        if not service:
            return False

        try:
            if not sheet_name:
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
                sheet_name = f"Leads_{timestamp}"

            # Convert leads to DataFrame for easier manipulation
            df = pd.DataFrame(leads)

            # Prepare data for Google Sheets
            headers = df.columns.tolist()
            values = [headers] + df.values.tolist()

            # Try to create a new sheet or use existing one
            try:
                # Create new sheet
                body = {
                    "requests": [{"addSheet": {"properties": {"title": sheet_name}}}]
                }
                service.spreadsheets().batchUpdate(
                    spreadsheetId=sheet_id, body=body
                ).execute()
                logger.info(f"Created new sheet: {sheet_name}")
            except Exception:
                # Sheet might already exist, continue with data upload
                logger.info(f"Using existing sheet: {sheet_name}")

            # Upload data
            range_name = f"{sheet_name}!A1"
            body = {"values": values}

            result = (
                service.spreadsheets()
                .values()
                .update(
                    spreadsheetId=sheet_id,
                    range=range_name,
                    valueInputOption="RAW",
                    body=body,
                )
                .execute()
            )

            logger.info(f"Successfully uploaded {len(leads)} leads to Google Sheets")
            return True

        except Exception as e:
            logger.error(f"Error uploading to Google Sheets: {e}")
            return False

    def scrape_industry(
        self,
        industry: str,
        city: str = "",
        state: str = "",
        max_records: int = 50,
        test_mode: bool = True,
        keywords: str = "",
        google_sheet_id: Optional[str] = None,
        google_sheet_name: Optional[str] = None,
        enable_enrichment: bool = True,
        hunter_api_key: Optional[str] = None,
        numverify_api_key: Optional[str] = None,
        export_format: str = "both",
        credentials_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Scrape leads for a specific industry with Phase 4 enrichment."""

        # Filter plugins by industry
        target_plugins = self.filter_plugins_by_industry(industry)

        if not target_plugins:
            return {
                "success": False,
                "error": f"No plugins found for industry: {industry}",
                "leads": [],
                "count": 0,
            }

        all_leads = []
        results_summary = []

        # Configuration for plugins
        config = {
            "city": city,
            "state": state,
            "max_records": max_records,
            "test_mode": test_mode,
            "keywords": keywords,
            "google_sheet_id": google_sheet_id,
            "google_sheet_name": google_sheet_name,
        }

        # Run each plugin for the industry
        for plugin in target_plugins:
            result = self.run_plugin(plugin, config)

            if result["success"] and result["leads"]:
                # Add metadata to each lead
                for lead in result["leads"]:
                    if "industry" not in lead:
                        lead["industry"] = industry
                    if "source" not in lead:
                        lead["source"] = plugin["site_name"]
                    if "Tag" not in lead:
                        lead["Tag"] = self.generate_tag(city, industry)

                all_leads.extend(result["leads"])
                results_summary.append(
                    {
                        "plugin": plugin["site_name"],
                        "count": result["count"],
                        "status": "success",
                    }
                )
            else:
                results_summary.append(
                    {
                        "plugin": plugin["site_name"],
                        "count": 0,
                        "status": f"failed: {result.get('error', 'unknown error')}",
                    }
                )

        # Phase 4: Lead enrichment
        enriched_leads = []
        if all_leads and enable_enrichment:
            try:
                enricher = LeadEnrichmentEngine(hunter_api_key, numverify_api_key)
                enriched_objects = enricher.enrich_leads_batch(all_leads)
                enriched_leads = [lead.__dict__ for lead in enriched_objects]
                logger.info(
                    f"Enriched {len(enriched_leads)} leads with advanced scoring"
                )
            except Exception as e:
                logger.warning(f"Lead enrichment failed, using raw data: {e}")
                enriched_leads = all_leads
        else:
            enriched_leads = all_leads

        # Save results if any leads found
        output_path = None
        google_sheets_uploaded = False
        google_sheets_stats = {}

        if enriched_leads:
            # Determine what to export based on export_format
            should_export_csv = export_format in ["csv", "both"]
            should_export_sheets = export_format in ["google_sheets", "both"]

            # Save to CSV if requested
            if should_export_csv:
                output_path = self.save_leads_to_csv(enriched_leads, industry, city)

            # Upload to Google Sheets if requested and configured
            if should_export_sheets and (
                google_sheet_id or os.getenv("DEFAULT_GOOGLE_SHEET_ID")
            ):
                try:
                    # Use provided sheet ID or fall back to environment variable
                    sheet_id = google_sheet_id or os.getenv("DEFAULT_GOOGLE_SHEET_ID")

                    if not sheet_id:
                        logger.warning(
                            "No Google Sheet ID provided - skipping Google Sheets export"
                        )
                    else:
                        # Initialize Google Sheets integration with custom credentials if provided
                        from google_sheets_integration import GoogleSheetsIntegration

                        if credentials_path:
                            sheets_integration = GoogleSheetsIntegration(
                                credentials_path=credentials_path
                            )
                        else:
                            sheets_integration = GoogleSheetsIntegration()

                        # Export using the integration
                        if sheets_integration.service:
                            sheet_name_final = (
                                google_sheet_name or f"{industry}_{city}_leads"
                            )

                            # Setup sheet headers and formatting
                            sheets_integration.setup_sheet_headers(
                                sheet_id, sheet_name_final
                            )

                            # Batch upsert leads with deduplication
                            inserted, updated, skipped = (
                                sheets_integration.batch_upsert_leads(
                                    sheet_id,
                                    enriched_leads,
                                    sheet_name_final,
                                    avoid_duplicates=True,
                                )
                            )

                            google_sheets_stats = {
                                "inserted": inserted,
                                "updated": updated,
                                "skipped": skipped,
                                "total_processed": len(enriched_leads),
                            }

                            google_sheets_uploaded = inserted > 0 or updated > 0

                            if google_sheets_uploaded:
                                sheet_url = sheets_integration.get_sheet_url(
                                    sheet_id, sheet_name_final
                                )
                                logger.info(
                                    f"✅ Google Sheets export successful: {sheet_url}"
                                )
                                print(f"📊 Google Sheets Link: {sheet_url}")

                            logger.info(
                                f"Google Sheets export stats: {google_sheets_stats}"
                            )
                        else:
                            logger.warning(
                                "Google Sheets service not initialized - authentication may be required"
                            )

                except Exception as e:
                    logger.warning(f"Google Sheets export failed: {e}")
                    # If Google Sheets export fails and CSV wasn't requested, create CSV as backup
                    if not should_export_csv and not output_path:
                        logger.info(
                            "Creating CSV backup since Google Sheets export failed"
                        )
                        output_path = self.save_leads_to_csv(
                            enriched_leads, industry, city
                        )

        return {
            "success": len(enriched_leads) > 0,
            "leads": enriched_leads,
            "count": len(enriched_leads),
            "enriched_count": len(enriched_leads) if enable_enrichment else 0,
            "industry": industry,
            "output_path": str(output_path) if output_path else None,
            "plugins_run": len(target_plugins),
            "results_summary": results_summary,
            "google_sheets_uploaded": google_sheets_uploaded,
            "google_sheets_stats": google_sheets_stats,
            "urgent_leads": sum(
                1 for lead in enriched_leads if lead.get("urgency_flag", False)
            ),
        }

    def interactive_mode(self) -> Dict[str, Any]:
        """Interactive mode for guided lead generation."""

        print("🏢 Universal Lead Generation - Interactive Mode")
        print("=" * 55)

        # Select industry
        print("\nAvailable Industries:")
        industries = self.get_available_industries()
        for i, industry in enumerate(industries, 1):
            print(f"  {i}. {industry.replace('_', ' ').title()}")
        print(f"  {len(industries) + 1}. All Industries")

        while True:
            try:
                choice = input(f"\nSelect industry [1-{len(industries) + 1}]: ").strip()
                choice_num = int(choice)

                if 1 <= choice_num <= len(industries):
                    selected_industry = industries[choice_num - 1]
                    break
                elif choice_num == len(industries) + 1:
                    selected_industry = "all"
                    break
                else:
                    print("Invalid choice. Please try again.")
            except ValueError:
                print("Please enter a valid number.")

        # Get location
        city = input("Enter city (optional): ").strip()
        state = input("Enter state (e.g., FL, CA): ").strip()

        # Get parameters
        try:
            max_records = int(input("Maximum records [50]: ").strip() or "50")
        except ValueError:
            max_records = 50

        # Test mode
        test_mode_input = input("Use test mode? [Y/n]: ").strip().lower()
        test_mode = test_mode_input != "n"

        # Keywords
        keywords = input("Keywords (optional): ").strip()

        print("\n🔄 Starting lead generation...")
        print(f"   Industry: {selected_industry.replace('_', ' ').title()}")
        print(f"   Location: {city}, {state}")
        print(f"   Mode: {'Test' if test_mode else 'Live'}")
        print(f"   Records: {max_records}")

        # Run scraping
        if selected_industry == "all":
            all_results = []
            for industry in industries:
                print(f"\n🔍 Processing {industry.replace('_', ' ').title()}...")
                result = self.scrape_industry(
                    industry=industry,
                    city=city,
                    state=state,
                    max_records=max_records,
                    test_mode=test_mode,
                    keywords=keywords,
                )
                all_results.append(result)

            # Combine results
            total_leads = sum(r["count"] for r in all_results)
            successful_industries = [r["industry"] for r in all_results if r["success"]]

            return {
                "success": total_leads > 0,
                "industries_processed": len(industries),
                "successful_industries": successful_industries,
                "total_leads": total_leads,
                "results": all_results,
            }
        else:
            return self.scrape_industry(
                industry=selected_industry,
                city=city,
                state=state,
                max_records=max_records,
                test_mode=test_mode,
                keywords=keywords,
            )


def main():
    """Main function with CLI argument parsing."""

    parser = argparse.ArgumentParser(
        description="Universal Lead Generation Automation - Phase 4 Optimize Prime",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python universal_automation.py --interactive
  python universal_automation.py --industry lawyers --city Miami --state FL
  python universal_automation.py --industry all --city Tampa --state FL --max-records 100
  python universal_automation.py --industry pool_contractors --test --verbose
        """,
    )

    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Run in interactive mode with guided setup",
    )

    parser.add_argument(
        "--industry",
        choices=AVAILABLE_INDUSTRIES + ["all"],
        help="Target industry for lead generation",
    )

    parser.add_argument("--city", help="Target city for lead search")

    parser.add_argument(
        "--state", help="Target state for lead search (e.g., FL, CA, NY)"
    )

    parser.add_argument("--keywords", help="Additional keywords for filtering results")

    parser.add_argument(
        "--max-records",
        "-m",
        type=int,
        default=50,
        help="Maximum number of records to scrape (default: 50)",
    )

    parser.add_argument(
        "--test", action="store_true", help="Run in test mode with simulated data"
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    parser.add_argument(
        "--list-industries",
        action="store_true",
        help="List available industries and exit",
    )

    parser.add_argument(
        "--google-sheet-id", help="Google Sheets ID for optional lead upload"
    )

    parser.add_argument(
        "--google-sheet-name", help="Name for the Google Sheet tab (optional)"
    )

    parser.add_argument(
        "--export",
        choices=["csv", "google_sheets", "both"],
        default="both",
        help="Export format: csv, google_sheets, or both (default: both)",
    )

    parser.add_argument(
        "--credentials",
        help="Path to Google OAuth credentials JSON file (default: client_secret_*.json in project root)",
    )

    args = parser.parse_args()

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Initialize automation
    automation = UniversalLeadAutomation()

    # Handle list industries
    if args.list_industries:
        print("Available Industries:")
        for industry in automation.get_available_industries():
            print(f"  - {industry.replace('_', ' ').title()}")
        return

    # Interactive mode
    if args.interactive:
        result = automation.interactive_mode()

        if result["success"]:
            if "industries_processed" in result:
                # Multi-industry result
                print("\n✅ Multi-industry processing completed!")
                print(f"📊 Industries processed: {result['industries_processed']}")
                print(f"📊 Total leads found: {result['total_leads']}")
                print(
                    f"✅ Successful industries: {', '.join(result['successful_industries'])}"
                )
            else:
                # Single industry result
                print("\n✅ Lead generation completed!")
                print(f"📊 Found {result['count']} leads")
                if result["output_path"]:
                    print(f"📁 Saved to: {result['output_path']}")
        else:
            print("\n❌ Lead generation failed")

        return

    # CLI mode - require industry
    if not args.industry:
        parser.error("--industry is required when not using --interactive mode")

    # Run CLI mode
    print("🏢 Universal Lead Generation - CLI Mode")
    print("=" * 45)

    result = automation.scrape_industry(
        industry=args.industry,
        city=args.city or "",
        state=args.state or "",
        max_records=args.max_records,
        test_mode=args.test,
        keywords=args.keywords or "",
        google_sheet_id=args.google_sheet_id,
        google_sheet_name=args.google_sheet_name,
        export_format=args.export,
        credentials_path=args.credentials,
    )

    # Display results
    if result["success"]:
        print("\n✅ Lead generation completed!")
        print(f"📊 Industry: {result['industry'].replace('_', ' ').title()}")
        print(f"📊 Found {result['count']} leads")
        print(f"🔧 Plugins run: {result['plugins_run']}")

        if result["output_path"]:
            print(f"📁 Saved to: {result['output_path']}")

        # Show plugin results
        if args.verbose and result["results_summary"]:
            print("\n📋 Plugin Results:")
            for summary in result["results_summary"]:
                status_icon = "✅" if summary["status"] == "success" else "❌"
                print(
                    f"  {status_icon} {summary['plugin']}: {summary['count']} leads ({summary['status']})"
                )
    else:
        print(f"\n❌ Lead generation failed: {result.get('error', 'Unknown error')}")
        sys.exit(1)


if __name__ == "__main__":
    main()
