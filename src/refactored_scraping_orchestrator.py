"""
Refactored scrape_industry function from universal_automation.py

Breaking down the monolithic function into smaller, testable components.
This addresses the complexity issue identified in the audit.
"""

from typing import Dict, Any, List, Optional
import os
import logging

logger = logging.getLogger(__name__)


class IndustryScrapingOrchestrator:
    """Orchestrates the complex industry scraping process."""
    
    def __init__(self, automation_engine):
        self.automation_engine = automation_engine
    
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
        credentials_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Main orchestration method - now much simpler."""
        
        # 1. Setup and validation
        config = self._build_plugin_config(
            city, state, max_records, test_mode, keywords, 
            google_sheet_id, google_sheet_name
        )
        
        target_plugins = self.automation_engine.filter_plugins_by_industry(industry)
        if not target_plugins:
            return self._build_error_result(f"No plugins found for industry: {industry}")
        
        # 2. Execute scraping
        raw_leads, results_summary = self._execute_plugin_scraping(
            target_plugins, industry, config
        )
        
        # 3. Enrich leads if enabled
        enriched_leads = self._enrich_leads_if_enabled(
            raw_leads, enable_enrichment, hunter_api_key, numverify_api_key
        )
        
        # 4. Export results
        export_results = self._handle_exports(
            enriched_leads, industry, city, export_format,
            google_sheet_id, google_sheet_name, credentials_path
        )
        
        # 5. Build final result
        return self._build_success_result(
            enriched_leads, industry, target_plugins, results_summary, 
            export_results, enable_enrichment
        )
    
    def _build_plugin_config(
        self, city: str, state: str, max_records: int, test_mode: bool,
        keywords: str, google_sheet_id: Optional[str], google_sheet_name: Optional[str]
    ) -> Dict[str, Any]:
        """Build configuration dictionary for plugins."""
        return {
            "city": city,
            "state": state,
            "max_records": max_records,
            "test_mode": test_mode,
            "keywords": keywords,
            "google_sheet_id": google_sheet_id,
            "google_sheet_name": google_sheet_name
        }
    
    def _execute_plugin_scraping(
        self, target_plugins: List[Dict], industry: str, config: Dict[str, Any]
    ) -> tuple[List[Dict], List[Dict]]:
        """Execute scraping across all target plugins."""
        all_leads = []
        results_summary = []
        
        for plugin in target_plugins:
            result = self.automation_engine.run_plugin(plugin, config)
            
            if result["success"] and result["leads"]:
                # Process and tag leads
                processed_leads = self._process_plugin_leads(
                    result["leads"], industry, plugin["site_name"]
                )
                all_leads.extend(processed_leads)
                
                results_summary.append({
                    "plugin": plugin["site_name"],
                    "count": result["count"],
                    "status": "success"
                })
            else:
                results_summary.append({
                    "plugin": plugin["site_name"],
                    "count": 0,
                    "status": f"failed: {result.get('error', 'unknown error')}"
                })
        
        return all_leads, results_summary
    
    def _process_plugin_leads(
        self, leads: List[Dict], industry: str, source: str
    ) -> List[Dict]:
        """Add metadata tags to leads from a plugin."""
        for lead in leads:
            if "industry" not in lead:
                lead["industry"] = industry
            if "source" not in lead:
                lead["source"] = source
            if "Tag" not in lead:
                lead["Tag"] = self.automation_engine.generate_tag(
                    lead.get("city", ""), industry
                )
        return leads
    
    def _enrich_leads_if_enabled(
        self, raw_leads: List[Dict], enable_enrichment: bool,
        hunter_api_key: Optional[str], numverify_api_key: Optional[str]
    ) -> List[Dict]:
        """Handle lead enrichment if enabled."""
        if not raw_leads or not enable_enrichment:
            return raw_leads
        
        try:
            from lead_enrichment_plugin import LeadEnrichmentEngine
            enricher = LeadEnrichmentEngine(hunter_api_key, numverify_api_key)
            enriched_objects = enricher.enrich_leads_batch(raw_leads)
            enriched_leads = [lead.__dict__ for lead in enriched_objects]
            logger.info(f"Enriched {len(enriched_leads)} leads with advanced scoring")
            return enriched_leads
        except Exception as e:
            logger.warning(f"Lead enrichment failed, using raw data: {e}")
            return raw_leads
    
    def _handle_exports(
        self, leads: List[Dict], industry: str, city: str, export_format: str,
        google_sheet_id: Optional[str], google_sheet_name: Optional[str],
        credentials_path: Optional[str]
    ) -> Dict[str, Any]:
        """Handle all export operations."""
        if not leads:
            return {"csv_path": None, "google_sheets_uploaded": False, "google_sheets_stats": {}}
        
        export_results = {
            "csv_path": None,
            "google_sheets_uploaded": False,
            "google_sheets_stats": {}
        }
        
        # CSV Export
        if export_format in ["csv", "both"]:
            export_results["csv_path"] = self.automation_engine.save_leads_to_csv(
                leads, industry, city
            )
        
        # Google Sheets Export
        if export_format in ["google_sheets", "both"]:
            sheets_result = self._handle_google_sheets_export(
                leads, industry, city, google_sheet_id, google_sheet_name, credentials_path
            )
            export_results.update(sheets_result)
            
            # Fallback CSV if Sheets fails and CSV wasn't requested
            if (not sheets_result["google_sheets_uploaded"] and 
                export_format == "google_sheets" and 
                not export_results["csv_path"]):
                logger.info("Creating CSV backup since Google Sheets export failed")
                export_results["csv_path"] = self.automation_engine.save_leads_to_csv(
                    leads, industry, city
                )
        
        return export_results
    
    def _handle_google_sheets_export(
        self, leads: List[Dict], industry: str, city: str,
        google_sheet_id: Optional[str], google_sheet_name: Optional[str],
        credentials_path: Optional[str]
    ) -> Dict[str, Any]:
        """Handle Google Sheets export with proper error handling."""
        result = {"google_sheets_uploaded": False, "google_sheets_stats": {}}
        
        try:
            # Get sheet ID (provided or from environment)
            sheet_id = google_sheet_id or os.getenv('DEFAULT_GOOGLE_SHEET_ID')
            if not sheet_id:
                logger.warning("No Google Sheet ID provided - skipping Google Sheets export")
                return result
            
            # Initialize Google Sheets integration
            from google_sheets_integration import GoogleSheetsIntegration
            
            if credentials_path:
                sheets_integration = GoogleSheetsIntegration(credentials_path=credentials_path)
            else:
                sheets_integration = GoogleSheetsIntegration()
            
            if not sheets_integration.service:
                logger.warning("Google Sheets service not initialized - authentication may be required")
                return result
            
            # Execute export
            sheet_name_final = google_sheet_name or f"{industry}_{city}_leads"
            
            # Setup and upsert
            sheets_integration.setup_sheet_headers(sheet_id, sheet_name_final)
            inserted, updated, skipped = sheets_integration.batch_upsert_leads(
                sheet_id, leads, sheet_name_final, avoid_duplicates=True
            )
            
            # Update results
            result["google_sheets_stats"] = {
                'inserted': inserted,
                'updated': updated,
                'skipped': skipped,
                'total_processed': len(leads)
            }
            
            result["google_sheets_uploaded"] = inserted > 0 or updated > 0
            
            if result["google_sheets_uploaded"]:
                sheet_url = sheets_integration.get_sheet_url(sheet_id, sheet_name_final)
                logger.info(f"✅ Google Sheets export successful: {sheet_url}")
                print(f"📊 Google Sheets Link: {sheet_url}")
            
            logger.info(f"Google Sheets export stats: {result['google_sheets_stats']}")
            
        except Exception as e:
            logger.warning(f"Google Sheets export failed: {e}")
        
        return result
    
    def _build_error_result(self, error_message: str) -> Dict[str, Any]:
        """Build standardized error result."""
        return {
            "success": False,
            "error": error_message,
            "leads": [],
            "count": 0
        }
    
    def _build_success_result(
        self, enriched_leads: List[Dict], industry: str, target_plugins: List[Dict],
        results_summary: List[Dict], export_results: Dict[str, Any], enable_enrichment: bool
    ) -> Dict[str, Any]:
        """Build standardized success result."""
        return {
            "success": len(enriched_leads) > 0,
            "leads": enriched_leads,
            "count": len(enriched_leads),
            "enriched_count": len(enriched_leads) if enable_enrichment else 0,
            "industry": industry,
            "output_path": str(export_results["csv_path"]) if export_results["csv_path"] else None,
            "plugins_run": len(target_plugins),
            "results_summary": results_summary,
            "google_sheets_uploaded": export_results["google_sheets_uploaded"],
            "google_sheets_stats": export_results["google_sheets_stats"],
            "urgent_leads": sum(1 for lead in enriched_leads if lead.get('urgency_flag', False))
        }