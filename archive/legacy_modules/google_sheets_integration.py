"""
Google Sheets Integration - Phase 4 Optimize Prime
Advanced Google Sheets integration with OAuth authentication, batch upsert, and duplicate handling
"""

import logging
import time
import os
import pickle
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
import hashlib
import json
from dataclasses import asdict

# Google Sheets API imports
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    import pandas as pd
    GOOGLE_SHEETS_AVAILABLE = True
except ImportError:
    GOOGLE_SHEETS_AVAILABLE = False

logger = logging.getLogger(__name__)


class GoogleSheetsIntegration:
    """Advanced Google Sheets integration with OAuth authentication and enterprise features."""

    def __init__(
        self,
        credentials_path: str = "client_secret_1020100796152-n6l4bloev9ha8to4mcbc6h3p8e1n1t3e.apps.googleusercontent.com.json",  # noqa: E501
        token_path: str = "token.pickle"
    ):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = None
        self.rate_limit_delay = 1.0  # Seconds between requests
        self.last_request_time = 0

        # Google Sheets API scopes
        self.scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive.readonly'
        ]

        # Lead schema for consistent column mapping
        self.lead_schema = [
            'name', 'company', 'email', 'phone', 'address', 'city', 'state', 'zip_code',
            'website', 'industry', 'business_type', 'description', 'source',
            'linkedin_url', 'facebook_url', 'twitter_url', 'instagram_url',
            'reviews_count', 'average_rating', 'lead_score', 'urgency_flag',
            'urgency_reason', 'email_verified', 'phone_verified',
            'created_date', 'last_updated', 'enrichment_version'
        ]

        self._initialize_service()

    def _initialize_service(self) -> bool:
        """Initialize Google Sheets API service with OAuth authentication."""
        if not GOOGLE_SHEETS_AVAILABLE:
            logger.error("Google Sheets integration not available. Install required packages:")
            logger.error("pip install google-api-python-client google-auth-oauthlib google-auth-httplib2 pandas")
            return False

        try:
            creds = None

            # Load existing token if available
            if os.path.exists(self.token_path):
                with open(self.token_path, 'rb') as token:
                    creds = pickle.load(token)

            # If there are no (valid) credentials available, request authentication
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    logger.info("Refreshing expired Google Sheets credentials...")
                    creds.refresh(Request())
                else:
                    logger.info("Starting OAuth authentication flow...")
                    logger.info("Please authenticate with sam@optimizeprimeconsulting.com when prompted")

                    if not os.path.exists(self.credentials_path):
                        logger.error(f"OAuth credentials file not found: {self.credentials_path}")
                        return False

                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, self.scopes
                    )
                    creds = flow.run_local_server(port=0)

                # Save the credentials for the next run
                with open(self.token_path, 'wb') as token:
                    pickle.dump(creds, token)
                    logger.info(f"Credentials saved to {self.token_path}")

            self.service = build('sheets', 'v4', credentials=creds)
            logger.info("Google Sheets API service initialized successfully with OAuth")
            return True

        except FileNotFoundError:
            logger.error(f"OAuth credentials file not found: {self.credentials_path}")
            logger.error("Please ensure the OAuth credentials JSON file is in the project root")
            return False

        except Exception as e:
            logger.error(f"Error initializing Google Sheets service: {e}")
            return False

    def _rate_limit(self):
        """Implement rate limiting to avoid API quota issues."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def _handle_api_error(self, error: HttpError, operation: str) -> bool:
        """Handle Google Sheets API errors with retry logic."""
        error_code = error.resp.status
        error_reason = error.error_details[0].get('reason', '') if error.error_details else ''

        logger.error(f"Google Sheets API error during {operation}: {error_code} - {error_reason}")

        # Handle rate limiting
        if error_code == 429 or 'quota' in error_reason.lower():
            logger.warning("Rate limit exceeded, waiting 60 seconds...")
            time.sleep(60)
            return True  # Retry

        # Handle temporary server errors
        if error_code >= 500:
            logger.warning("Server error, waiting 30 seconds...")
            time.sleep(30)
            return True  # Retry

        return False  # Don't retry

    def create_or_get_spreadsheet(self, spreadsheet_name: str) -> Optional[str]:
        """Create a new spreadsheet or get existing one by name."""
        if not self.service:
            return None

        try:
            # Try to find existing spreadsheet (requires Drive API access)
            # For now, return None to force manual spreadsheet creation
            logger.warning(f"Please create spreadsheet '{spreadsheet_name}' manually and provide the ID")
            return None

        except Exception as e:
            logger.error(f"Error creating/finding spreadsheet: {e}")
            return None

    def setup_sheet_headers(self, spreadsheet_id: str, sheet_name: str = "Leads") -> bool:
        """Setup the sheet with proper headers and formatting."""
        if not self.service:
            return False

        try:
            self._rate_limit()

            # Check if sheet exists, create if not
            try:
                sheet_metadata = self.service.spreadsheets().get(
                    spreadsheetId=spreadsheet_id
                ).execute()

                sheet_exists = any(
                    sheet['properties']['title'] == sheet_name
                    for sheet in sheet_metadata['sheets']
                )

                if not sheet_exists:
                    # Create new sheet
                    body = {
                        'requests': [{
                            'addSheet': {
                                'properties': {
                                    'title': sheet_name
                                }
                            }
                        }]
                    }
                    self.service.spreadsheets().batchUpdate(
                        spreadsheetId=spreadsheet_id,
                        body=body
                    ).execute()
                    logger.info(f"Created new sheet: {sheet_name}")

            except HttpError as e:
                if not self._handle_api_error(e, "sheet creation"):
                    return False

            # Set up headers
            self._rate_limit()
            headers_range = f"{sheet_name}!A1:{chr(65 + len(self.lead_schema) - 1)}1"

            body = {
                'values': [self.lead_schema]
            }

            self.service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=headers_range,
                valueInputOption='RAW',
                body=body
            ).execute()

            # Format headers (bold, freeze row)
            self._rate_limit()
            format_body = {
                'requests': [
                    {
                        'repeatCell': {
                            'range': {
                                'sheetId': 0,  # Assuming first sheet
                                'startRowIndex': 0,
                                'endRowIndex': 1,
                                'startColumnIndex': 0,
                                'endColumnIndex': len(self.lead_schema)
                            },
                            'cell': {
                                'userEnteredFormat': {
                                    'textFormat': {'bold': True},
                                    'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}
                                }
                            },
                            'fields': 'userEnteredFormat(textFormat,backgroundColor)'
                        }
                    },
                    {
                        'updateSheetProperties': {
                            'properties': {
                                'sheetId': 0,
                                'gridProperties': {
                                    'frozenRowCount': 1
                                }
                            },
                            'fields': 'gridProperties.frozenRowCount'
                        }
                    }
                ]
            }

            self.service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=format_body
            ).execute()

            logger.info(f"Successfully setup headers for sheet: {sheet_name}")
            return True

        except HttpError as e:
            if self._handle_api_error(e, "header setup"):
                return self.setup_sheet_headers(spreadsheet_id, sheet_name)  # Retry
            return False
        except Exception as e:
            logger.error(f"Error setting up sheet headers: {e}")
            return False

    def get_existing_leads(self, spreadsheet_id: str, sheet_name: str = "Leads") -> List[Dict[str, Any]]:
        """Get all existing leads from the sheet to check for duplicates."""
        if not self.service:
            return []

        try:
            self._rate_limit()

            # Get all data from sheet
            range_name = f"{sheet_name}!A:Z"
            result = self.service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=range_name
            ).execute()

            values = result.get('values', [])
            if not values or len(values) < 2:  # No data beyond headers
                return []

            # Convert to list of dictionaries
            headers = values[0]
            leads = []

            for row in values[1:]:
                # Pad row to match headers length
                row_data = row + [''] * (len(headers) - len(row))
                lead_dict = dict(zip(headers, row_data))
                leads.append(lead_dict)

            logger.info(f"Retrieved {len(leads)} existing leads from sheet")
            return leads

        except HttpError as e:
            if self._handle_api_error(e, "getting existing leads"):
                return self.get_existing_leads(spreadsheet_id, sheet_name)  # Retry
            return []
        except Exception as e:
            logger.error(f"Error getting existing leads: {e}")
            return []

    def _generate_lead_hash(self, lead_data: Dict[str, Any]) -> str:
        """Generate a hash for duplicate detection based on email/phone."""
        email = str(lead_data.get('email', '')).strip().lower()
        phone = str(lead_data.get('phone', '')).strip()
        company = str(lead_data.get('company', '')).strip().lower()

        # Remove non-digits from phone
        import re
        phone_digits = re.sub(r'[^\d]', '', phone)

        # Create hash from key identifying fields
        hash_string = f"{email}|{phone_digits}|{company}"
        return hashlib.md5(hash_string.encode()).hexdigest()

    def batch_upsert_leads(
        self,
        spreadsheet_id: str,
        leads: List[Dict[str, Any]],
        sheet_name: str = "Leads",
        avoid_duplicates: bool = True
    ) -> Tuple[int, int, int]:
        """
        Batch upsert leads with duplicate detection.
        Returns: (inserted, updated, skipped)
        """
        if not self.service or not leads:
            return 0, 0, 0

        # Get existing leads for duplicate detection
        existing_leads = []
        existing_hashes = set()

        if avoid_duplicates:
            existing_leads = self.get_existing_leads(spreadsheet_id, sheet_name)
            existing_hashes = {
                self._generate_lead_hash(lead) for lead in existing_leads
            }

        # Process new leads
        new_leads = []
        updated_leads = []
        skipped_count = 0

        for lead_data in leads:
            lead_hash = self._generate_lead_hash(lead_data)

            if avoid_duplicates and lead_hash in existing_hashes:
                skipped_count += 1
                logger.debug(f"Skipping duplicate lead: {lead_data.get('company', 'Unknown')}")
                continue

            # Ensure all schema fields are present
            formatted_lead = {}
            for field in self.lead_schema:
                formatted_lead[field] = str(lead_data.get(field, ''))

            new_leads.append(formatted_lead)

        if not new_leads:
            logger.info(f"No new leads to insert. Skipped {skipped_count} duplicates.")
            return 0, 0, skipped_count

        # Insert new leads
        try:
            self._rate_limit()

            # Convert leads to rows
            rows = []
            for lead in new_leads:
                row = [lead[field] for field in self.lead_schema]
                rows.append(row)

            # Find the next empty row
            existing_row_count = len(existing_leads) + 1  # +1 for header
            start_row = existing_row_count + 1
            end_row = start_row + len(rows) - 1

            range_name = f"{sheet_name}!A{start_row}:{chr(65 + len(self.lead_schema) - 1)}{end_row}"

            body = {
                'values': rows
            }

            self.service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()

            inserted_count = len(new_leads)
            logger.info(f"Successfully inserted {inserted_count} new leads to Google Sheets")

            return inserted_count, 0, skipped_count

        except HttpError as e:
            if self._handle_api_error(e, "batch upsert"):
                return self.batch_upsert_leads(spreadsheet_id, leads, sheet_name, avoid_duplicates)
            return 0, 0, skipped_count
        except Exception as e:
            logger.error(f"Error during batch upsert: {e}")
            return 0, 0, skipped_count

    def tag_leads_by_industry(
        self,
        spreadsheet_id: str,
        sheet_name: str = "Leads"
    ) -> bool:
        """Add conditional formatting and filters for industry-based tagging."""
        if not self.service:
            return False

        try:
            self._rate_limit()

            # Get sheet ID
            sheet_metadata = self.service.spreadsheets().get(
                spreadsheetId=spreadsheet_id
            ).execute()

            sheet_id = None
            for sheet in sheet_metadata['sheets']:
                if sheet['properties']['title'] == sheet_name:
                    sheet_id = sheet['properties']['sheetId']
                    break

            if sheet_id is None:
                logger.error(f"Sheet '{sheet_name}' not found")
                return False

            # Industry column index (assuming it's in the schema)
            industry_col_index = self.lead_schema.index('industry') if 'industry' in self.lead_schema else None
            urgency_col_index = self.lead_schema.index('urgency_flag') if 'urgency_flag' in self.lead_schema else None

            format_requests = []

            # Color code by urgency flag
            if urgency_col_index is not None:
                format_requests.append({
                    'addConditionalFormatRule': {
                        'rule': {
                            'ranges': [{
                                'sheetId': sheet_id,
                                'startRowIndex': 1,  # Skip header
                                'startColumnIndex': 0,
                                'endColumnIndex': len(self.lead_schema)
                            }],
                            'booleanRule': {
                                'condition': {
                                    'type': 'TEXT_EQ',
                                    'values': [{'userEnteredValue': 'True'}]
                                },
                                'format': {
                                    'backgroundColor': {'red': 1.0, 'green': 0.8, 'blue': 0.8}
                                }
                            }
                        },
                        'index': 0
                    }
                })

            # Add filters
            format_requests.append({
                'setBasicFilter': {
                    'filter': {
                        'range': {
                            'sheetId': sheet_id,
                            'startRowIndex': 0,
                            'startColumnIndex': 0,
                            'endColumnIndex': len(self.lead_schema)
                        }
                    }
                }
            })

            if format_requests:
                body = {'requests': format_requests}
                self.service.spreadsheets().batchUpdate(
                    spreadsheetId=spreadsheet_id,
                    body=body
                ).execute()

                logger.info("Successfully applied industry tagging and filters")

            return True

        except Exception as e:
            logger.error(f"Error applying industry tagging: {e}")
            return False

    def get_sheet_url(self, spreadsheet_id: str, sheet_name: str = "Leads") -> str:
        """Generate direct URL to the Google Sheet."""
        if sheet_name and sheet_name != "Sheet1":
            # Try to get the sheet GID for more precise linking
            return f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit#gid=0"
        return f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit"


def export_leads_to_sheets(
    leads: List[Dict[str, Any]],
    spreadsheet_id: str,
    sheet_name: str = "Leads",
    avoid_duplicates: bool = True,
    setup_formatting: bool = True
) -> Tuple[bool, Dict[str, int]]:
    """
    High-level function to export leads to Google Sheets.
    Returns: (success, stats_dict)
    """
    sheets = GoogleSheetsIntegration()

    if not sheets.service:
        return False, {'error': 'Google Sheets service not available'}

    # Setup sheet headers if needed
    if setup_formatting:
        sheets.setup_sheet_headers(spreadsheet_id, sheet_name)
        sheets.tag_leads_by_industry(spreadsheet_id, sheet_name)

    # Batch upsert leads
    inserted, updated, skipped = sheets.batch_upsert_leads(
        spreadsheet_id, leads, sheet_name, avoid_duplicates
    )

    stats = {
        'inserted': inserted,
        'updated': updated,
        'skipped': skipped,
        'total_processed': len(leads)
    }

    success = inserted > 0 or updated > 0

    if success:
        sheet_url = sheets.get_sheet_url(spreadsheet_id, sheet_name)
        logger.info(f"Google Sheets export complete. View at: {sheet_url}")

    return success, stats


if __name__ == "__main__":
    # Test the Google Sheets integration
    import argparse

    parser = argparse.ArgumentParser(description="Google Sheets Integration Test")
    parser.add_argument("spreadsheet_id", help="Google Sheets spreadsheet ID")
    parser.add_argument("--csv-file", help="CSV file to upload")
    parser.add_argument("--sheet-name", default="Leads", help="Sheet name")
    parser.add_argument("--setup-only", action="store_true", help="Only setup headers")

    args = parser.parse_args()

    sheets = GoogleSheetsIntegration()

    if args.setup_only:
        success = sheets.setup_sheet_headers(args.spreadsheet_id, args.sheet_name)
        print(f"Setup headers: {'✅' if success else '❌'}")
    elif args.csv_file:
        # Load CSV and export
        import pandas as pd
        df = pd.read_csv(args.csv_file)
        leads = df.to_dict('records')

        success, stats = export_leads_to_sheets(
            leads, args.spreadsheet_id, args.sheet_name
        )

        print(f"Export result: {'✅' if success else '❌'}")
        print(f"Stats: {stats}")
    else:
        print("Please provide --csv-file or use --setup-only")
