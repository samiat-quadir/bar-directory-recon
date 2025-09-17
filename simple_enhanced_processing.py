#!/usr/bin/env python3
"""
Simple Enhanced Processing Script with Google Sheets Export
"""

import json
import os
from datetime import datetime
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def load_and_process_data():
    """Load existing data and process with Google Sheets export."""
    print("=" * 60)
    print("PROPERTY DATA PROCESSING & EXPORT")
    print("=" * 60)

    # Load Hallandale data
    hallandale_file = Path("outputs/hallandale/hallandale_properties_enriched.csv")
    priority_file = Path("outputs/priority_leads.csv")

    results = {}

    if hallandale_file.exists():
        print("✅ Loading Hallandale data...")
        df = pd.read_csv(hallandale_file)

        # Analyze data
        total_records = len(df)
        email_records = (
            df["owner_email"].notna().sum() if "owner_email" in df.columns else 0
        )
        phone_records = (
            df["owner_phone"].notna().sum() if "owner_phone" in df.columns else 0
        )

        print(f"   • Total records: {total_records}")
        print(
            f"   • Records with email: {email_records} ({email_records/total_records*100:.1f}%)"
        )
        print(
            f"   • Records with phone: {phone_records} ({phone_records/total_records*100:.1f}%)"
        )

        # Export to Google Sheets
        export_success = export_to_sheets(df, "Hallandale_Properties")

        results["hallandale"] = {
            "total_records": int(total_records),
            "email_records": int(email_records),
            "phone_records": int(phone_records),
            "export_success": export_success,
        }

    if priority_file.exists():
        print("\n✅ Loading Priority Leads...")
        df = pd.read_csv(priority_file)

        total_records = len(df)
        print(f"   • Total priority leads: {total_records}")

        # Export to Google Sheets
        export_success = export_to_sheets(df, "Priority_Leads")

        results["priority_leads"] = {
            "total_records": int(total_records),
            "export_success": export_success,
        }

    return results


def export_to_sheets(df, sheet_name):
    """Simple Google Sheets export."""
    try:
        sheet_id = os.getenv("SHEET_ID")
        credentials_path = os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH")

        if not sheet_id or not credentials_path:
            print(f"   ⚠️ Google Sheets not configured for {sheet_name}")
            return False

        if not Path(credentials_path).exists():
            print(f"   ⚠️ Credentials file not found for {sheet_name}")
            return False

        import gspread
        from google.oauth2.service_account import Credentials

        # Setup
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]

        creds = Credentials.from_service_account_file(credentials_path, scopes=scope)
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_key(sheet_id)

        # Create/update worksheet
        try:
            worksheet = spreadsheet.worksheet(sheet_name)
            worksheet.clear()
        except gspread.WorksheetNotFound:
            worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=20)

        # Convert DataFrame to strings
        export_df = df.astype(str)

        # Export
        data = [export_df.columns.tolist()] + export_df.values.tolist()
        worksheet.update(data)

        print(f"   ✅ Exported to Google Sheets: {sheet_name}")
        return True

    except Exception as e:
        print(f"   ❌ Export failed for {sheet_name}: {str(e)}")
        return False


def check_missing_pdfs():
    """Check for additional data sources and suggest next steps."""
    print("\n" + "=" * 60)
    print("ADDITIONAL DATA SOURCE ANALYSIS")
    print("=" * 60)

    # Check for additional PDFs
    pdf_locations = ["PDF PARSER", "input", "inputs", "data", "documents"]

    found_pdfs = []
    for location in pdf_locations:
        path = Path(location)
        if path.exists():
            pdfs = list(path.glob("*.pdf"))
            if pdfs:
                found_pdfs.extend([(location, pdf.name) for pdf in pdfs])

    if found_pdfs:
        print("📄 Found PDF files:")
        for location, filename in found_pdfs:
            print(f"   • {location}/{filename}")
    else:
        print("❌ No additional PDF files found")

    # Suggest public data sources
    print("\n🔍 SUGGESTED PUBLIC DATA SOURCES:")
    suggestions = [
        "Miami-Dade Property Appraiser: www.miamidade.gov/pa",
        "Broward Property Appraiser: bcpa.net",
        "Palm Beach Property Appraiser: pbcgov.com/papa",
        "Hillsborough County Property Search: hcpafl.org",
        "Orange County Property Search: ocpafl.org",
        "FL Dept. of Business & Professional Regulation: myfloridalicense.com",
        "FL Division of Corporations: dos.myflorida.com/sunbiz",
    ]

    for suggestion in suggestions:
        print(f"   • {suggestion}")

    return found_pdfs


def generate_final_summary(results, found_pdfs):
    """Generate final summary report."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Create summary
    summary = {
        "timestamp": timestamp,
        "processing_results": results,
        "additional_pdfs_found": len(found_pdfs),
        "recommendations": [],
    }

    # Add recommendations
    total_exported = sum(
        1 for city_data in results.values() if city_data.get("export_success", False)
    )
    total_cities = len(results)

    if total_exported < total_cities:
        summary["recommendations"].append(
            "Fix Google Sheets configuration for failed exports"
        )

    if not found_pdfs:
        summary["recommendations"].append(
            "Acquire additional city/county property data"
        )
        summary["recommendations"].append("Check suggested public data sources")

    # Check API configuration
    api_missing = []
    if not os.getenv("HUNTER_API_KEY"):
        api_missing.append("Hunter.io")
    if not os.getenv("ZEROBOUNCE_API_KEY"):
        api_missing.append("ZeroBounce")

    if api_missing:
        summary["recommendations"].append(
            f"Configure missing APIs: {', '.join(api_missing)}"
        )

    # Save summary
    summary_file = f"outputs/processing_summary_{timestamp}.json"
    with open(summary_file, "w") as f:
        json.dump(summary, f, indent=2)

    # Create text report
    report_lines = [
        "=" * 60,
        "PROCESSING SUMMARY REPORT",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "=" * 60,
        "",
        "RESULTS:",
    ]

    for city, data in results.items():
        report_lines.extend(
            [
                f"\n{city.upper()}:",
                f"  • Records processed: {data['total_records']}",
                f"  • Google Sheets export: {'✅ Success' if data.get('export_success') else '❌ Failed'}",
            ]
        )

        if "email_records" in data:
            report_lines.append(
                f"  • Email completion: {data['email_records']}/{data['total_records']}"
            )
        if "phone_records" in data:
            report_lines.append(
                f"  • Phone completion: {data['phone_records']}/{data['total_records']}"
            )

    if summary["recommendations"]:
        report_lines.extend(
            [
                "",
                "RECOMMENDATIONS:",
            ]
        )
        for rec in summary["recommendations"]:
            report_lines.append(f"  • {rec}")

    report_lines.extend(["", f"Additional PDFs found: {len(found_pdfs)}", "", "=" * 60])

    report_file = f"outputs/processing_report_{timestamp}.txt"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    print(f"\n✅ Summary saved: {summary_file}")
    print(f"✅ Report saved: {report_file}")

    return summary


def main():
    """Main function."""
    try:
        # Process existing data
        results = load_and_process_data()

        # Check for additional data sources
        found_pdfs = check_missing_pdfs()

        # Generate summary
        summary = generate_final_summary(results, found_pdfs)

        # Print final status
        print("\n" + "=" * 60)
        print("PROCESSING COMPLETE")
        print("=" * 60)

        total_records = sum(data["total_records"] for data in results.values())
        successful_exports = sum(
            1 for data in results.values() if data.get("export_success")
        )

        print(f"Cities processed: {len(results)}")
        print(f"Total records: {total_records}")
        print(f"Google Sheets exports: {successful_exports}/{len(results)}")
        print(f"Additional PDFs available: {len(found_pdfs)}")
        print(f"Recommendations: {len(summary['recommendations'])}")

        if summary["recommendations"]:
            print("\nNext steps:")
            for i, rec in enumerate(summary["recommendations"][:3], 1):
                print(f"  {i}. {rec}")

    except Exception as e:
        print(f"❌ Processing failed: {str(e)}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
