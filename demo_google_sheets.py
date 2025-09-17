#!/usr/bin/env python3
"""
Google Sheets Integration Demo
Demonstrates OAuth authentication and basic Google Sheets export functionality
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def demo_oauth_flow():
    """Demonstrate the OAuth authentication flow."""

    print("🔐 Google Sheets OAuth Demo")
    print("=" * 35)

    try:
        from google_sheets_integration import GoogleSheetsIntegration

        print("📦 Importing Google Sheets integration...")

        # Use the OAuth credentials file
        credentials_path = "client_secret_1020100796152-n6l4bloev9ha8to4mcbc6h3p8e1n1t3e.apps.googleusercontent.com.json"

        if not os.path.exists(credentials_path):
            print(f"❌ Credentials file not found: {credentials_path}")
            return False

        print(f"📁 Found credentials file: {credentials_path}")

        # Initialize the integration (this will trigger OAuth if needed)
        print("🔑 Initializing Google Sheets integration...")
        print("   This may open a browser window for authentication...")
        print("   Please authenticate with: sam@optimizeprimeconsulting.com")

        sheets = GoogleSheetsIntegration(credentials_path=credentials_path)

        if sheets.service:
            print("✅ Google Sheets service initialized successfully!")
            print("🎉 OAuth authentication completed!")

            # Test creating sample data
            sample_leads = [
                {
                    "name": "John Smith",
                    "company": "ABC Real Estate",
                    "email": "john@abcrealestate.com",
                    "phone": "(555) 123-4567",
                    "city": "Miami",
                    "state": "FL",
                    "industry": "real_estate",
                    "lead_score": 85,
                    "urgency_flag": True,
                    "urgency_reason": "High lead score and recent activity",
                },
                {
                    "name": "Sarah Johnson",
                    "company": "Sunshine Pools",
                    "email": "sarah@sunshinepool.com",
                    "phone": "(555) 987-6543",
                    "city": "Tampa",
                    "state": "FL",
                    "industry": "pool_contractors",
                    "lead_score": 92,
                    "urgency_flag": True,
                    "urgency_reason": "Highest scoring lead with verified contact",
                },
            ]

            print(f"📊 Created {len(sample_leads)} sample leads for testing")

            # Ask user if they want to test with a real spreadsheet
            print("\n" + "=" * 50)
            print("To complete the test, you'll need a Google Spreadsheet ID.")
            print("Create a new Google Sheet and copy its ID from the URL:")
            print("https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit")
            print("")
            sheet_id = input("Enter Google Sheet ID (or press Enter to skip): ").strip()

            if sheet_id:
                try:
                    # Test the export
                    print(f"📤 Testing export to Google Sheet: {sheet_id}")

                    sheet_name = "Demo_Leads"

                    # Setup headers
                    if sheets.setup_sheet_headers(sheet_id, sheet_name):
                        print("✅ Sheet headers configured")

                    # Export the sample leads
                    inserted, updated, skipped = sheets.batch_upsert_leads(
                        sheet_id, sample_leads, sheet_name, avoid_duplicates=True
                    )

                    print("📊 Export Results:")
                    print(f"   📝 Inserted: {inserted}")
                    print(f"   🔄 Updated: {updated}")
                    print(f"   ⏭️ Skipped: {skipped}")

                    if inserted > 0 or updated > 0:
                        sheet_url = sheets.get_sheet_url(sheet_id, sheet_name)
                        print(f"🎉 Success! View your sheet at: {sheet_url}")
                        return True
                    else:
                        print("⚠️ No data was written to the sheet")
                        return False

                except Exception as e:
                    print(f"❌ Export failed: {e}")
                    return False
            else:
                print("ℹ️ Spreadsheet test skipped")
                return True

        else:
            print("❌ Failed to initialize Google Sheets service")
            return False

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please install Google API packages:")
        print(
            "pip install google-api-python-client google-auth-oauthlib google-auth-httplib2"
        )
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def demo_cli_integration():
    """Demonstrate the CLI integration with the new export flags."""

    print("\n🖥️ CLI Integration Demo")
    print("=" * 25)

    print("The universal_automation.py script now supports:")
    print("")
    print("📋 New CLI Arguments:")
    print("   --export [csv|google_sheets|both]  # Export format selection")
    print("   --credentials <path>               # OAuth credentials file path")
    print("")
    print("📝 Example Commands:")
    print("")
    print("1. Export to Google Sheets only:")
    print(
        "   python universal_automation.py --industry pool_contractors --city Miami --state FL --export google_sheets"
    )
    print("")
    print("2. Export to both CSV and Google Sheets:")
    print(
        "   python universal_automation.py --industry real_estate --city Tampa --state FL --export both"
    )
    print("")
    print("3. Use custom credentials file:")
    print(
        "   python universal_automation.py --industry lawyers --city Orlando --state FL --export google_sheets --credentials path/to/creds.json"
    )
    print("")
    print("📊 Environment Variables:")
    print("   DEFAULT_GOOGLE_SHEET_ID=your-sheet-id-here")
    print("   GOOGLE_CREDENTIALS_PATH=path/to/credentials.json")
    print("")

    return True


def demo_automation_script():
    """Demonstrate the PowerShell automation script."""

    print("\n🤖 Automation Script Demo")
    print("=" * 28)

    script_path = project_root / "Automated-GoogleSheets-Export.ps1"

    if script_path.exists():
        print(f"✅ Found automation script: {script_path}")
        print("")
        print("🔧 PowerShell Automation Features:")
        print("   ✓ Scheduled execution support")
        print("   ✓ Automatic log management")
        print("   ✓ Environment variable setup")
        print("   ✓ Error handling and retry logic")
        print("   ✓ Output file tracking")
        print("   ✓ Google Sheets link extraction")
        print("")
        print("📝 Example Usage:")
        print(
            f'   PowerShell -ExecutionPolicy Bypass -File "{script_path}" -Industry "pool_contractors" -City "Miami" -State "FL" -GoogleSheetId "your-sheet-id"'
        )
        print("")
        print(
            "⏰ For scheduled runs, use Windows Task Scheduler to run this PowerShell script"
        )

        return True
    else:
        print(f"❌ Automation script not found: {script_path}")
        return False


if __name__ == "__main__":
    print("🚀 Google Sheets Integration Complete Demo")
    print("=" * 50)

    # Run all demos
    results = []

    results.append(demo_oauth_flow())
    results.append(demo_cli_integration())
    results.append(demo_automation_script())

    # Final summary
    print("\n" + "=" * 50)
    print("📊 Demo Summary:")
    print(f"   ✅ Successful demos: {sum(results)}")
    print(f"   ❌ Failed demos: {len(results) - sum(results)}")

    if all(results):
        print("\n🎉 Google Sheets integration is fully operational!")
        print("")
        print("📋 Next Steps:")
        print("1. Run your first automation:")
        print(
            "   python universal_automation.py --industry pool_contractors --city Miami --state FL --export google_sheets"
        )
        print("")
        print("2. Set up scheduled automation:")
        print("   Use Windows Task Scheduler with Automated-GoogleSheets-Export.ps1")
        print("")
        print("3. Check logs in the /logs/ directory for all activity")
        print("")
        sys.exit(0)
    else:
        print("\n⚠️ Some demos failed. Please check the setup and try again.")
        sys.exit(1)
