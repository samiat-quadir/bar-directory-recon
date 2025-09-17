#!/usr/bin/env python3
"""
Enhanced Property Processing Pipeline
Processes existing data with Google Sheets export and comprehensive reporting
"""

import json
import os
import sys

# Removed unused import: time
from datetime import datetime
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.append("src")


def load_existing_data() -> dict:
    """Load existing processed data."""
    hallandale_file = Path("outputs/hallandale/hallandale_properties_enriched.csv")
    priority_file = Path("outputs/priority_leads.csv")

    data = {}

    if hallandale_file.exists():
        data["hallandale"] = pd.read_csv(hallandale_file)
        print(f"✅ Loaded Hallandale data: {len(data['hallandale'])} records")

    if priority_file.exists():
        data["priority_leads"] = pd.read_csv(priority_file)
        print(f"✅ Loaded priority leads: {len(data['priority_leads'])} records")

    return data


def analyze_data_quality(df: pd.DataFrame, city_name: str = "Unknown") -> dict:
    """Analyze data quality and completeness."""
    analysis = {
        "city": city_name,
        "total_records": len(df),
        "timestamp": datetime.now().isoformat(),
    }

    # Basic completeness metrics
    if "owner_email" in df.columns:
        analysis["records_with_email"] = df["owner_email"].notna().sum()
        analysis["email_completion_rate"] = (
            analysis["records_with_email"] / analysis["total_records"]
        ) * 100

    if "owner_phone" in df.columns:
        analysis["records_with_phone"] = df["owner_phone"].notna().sum()
        analysis["phone_completion_rate"] = (
            analysis["records_with_phone"] / analysis["total_records"]
        ) * 100

    if "data_quality_score" in df.columns:
        analysis["avg_quality_score"] = df["data_quality_score"].mean()
        analysis["high_quality_records"] = (df["data_quality_score"] >= 80).sum()

    if "is_corporate" in df.columns:
        analysis["corporate_entities"] = df["is_corporate"].sum()
        analysis["individual_owners"] = (~df["is_corporate"]).sum()

    if "priority_flag" in df.columns:
        analysis["priority_records"] = (
            df["priority_flag"].sum() if df["priority_flag"].dtype == bool else 0
        )

    return analysis


def export_to_google_sheets(df: pd.DataFrame, sheet_name: str, analysis: dict) -> bool:
    """Export data to Google Sheets."""
    try:
        # Check if Google Sheets credentials are available
        sheet_id = os.getenv("SHEET_ID")
        credentials_path = os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH")

        if not sheet_id or not credentials_path:
            print("⚠️ Google Sheets not configured - skipping export")
            return False

        if not Path(credentials_path).exists():
            print("⚠️ Google Sheets credentials file not found - skipping export")
            return False

        # Import Google Sheets modules
        try:
            import gspread
            from google.oauth2.service_account import Credentials

            # Set up credentials
            scope = [
                "https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/drive",
            ]

            creds = Credentials.from_service_account_file(credentials_path, scopes=scope)
            client = gspread.authorize(creds)

            # Open spreadsheet
            spreadsheet = client.open_by_key(sheet_id)

            # Create or update worksheet
            try:
                worksheet = spreadsheet.worksheet(sheet_name)
                worksheet.clear()
            except gspread.WorksheetNotFound:
                worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=20)

            # Prepare data for export
            export_df = df.copy()

            # Convert lists and dicts to strings for Google Sheets compatibility
            for col in export_df.columns:
                if export_df[col].dtype == "object":
                    export_df[col] = export_df[col].astype(str)

            # Export data
            worksheet.update([export_df.columns.values.tolist()] + export_df.values.tolist())

            # Add summary information
            summary_row = len(export_df) + 3
            worksheet.update(
                f"A{summary_row}",
                f'Summary - Total Records: {analysis["total_records"]}',
            )
            worksheet.update(
                f"A{summary_row + 1}",
                f'Quality Score Average: {analysis.get("avg_quality_score", "N/A")}',
            )
            worksheet.update(
                f"A{summary_row + 2}",
                f'Export Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
            )

            print(f"✅ Exported {len(export_df)} records to Google Sheets: {sheet_name}")
            return True

        except ImportError:
            print("⚠️ Google Sheets libraries not available - skipping export")
            return False
        except Exception as e:
            print(f"⚠️ Google Sheets export failed: {str(e)}")
            return False

    except Exception as e:
        print(f"⚠️ Google Sheets export failed with unexpected error: {str(e)}")
        return False


def check_api_status() -> dict:
    """Check status of enrichment APIs."""
    api_status = {
        "google_sheets": False,
        "hunter_io": False,
        "zerobounce": False,
        "gmail": False,
        "timestamp": datetime.now().isoformat(),
    }

    # Check Google Sheets
    sheet_id = os.getenv("SHEET_ID")
    credentials_path = os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH")
    if sheet_id and credentials_path and Path(credentials_path).exists():
        api_status["google_sheets"] = True

    # Check for Hunter.io API key
    if os.getenv("HUNTER_API_KEY"):
        api_status["hunter_io"] = True

    # Check for ZeroBounce API key
    if os.getenv("ZEROBOUNCE_API_KEY"):
        api_status["zerobounce"] = True

    # Check Gmail configuration
    gmail_creds = os.getenv("GMAIL_CREDENTIALS_PATH")
    if gmail_creds and Path(gmail_creds).exists():
        api_status["gmail"] = True

    return api_status


def generate_processing_summary(
    data: dict, analyses: list, api_status: dict, export_results: dict
) -> dict:
    """Generate comprehensive processing summary."""
    summary = {
        "processing_date": datetime.now().isoformat(),
        "total_cities_processed": len(data),
        "total_records_processed": sum(analysis["total_records"] for analysis in analyses),
        "api_status": api_status,
        "export_results": export_results,
        "city_analyses": analyses,
        "recommendations": [],
    }

    # Generate recommendations
    if not api_status["hunter_io"]:
        summary["recommendations"].append("Configure Hunter.io API for enhanced email discovery")

    if not api_status["zerobounce"]:
        summary["recommendations"].append("Configure ZeroBounce API for email validation")

    if not api_status["google_sheets"]:
        summary["recommendations"].append("Verify Google Sheets credentials and configuration")

    for analysis in analyses:
        if analysis.get("email_completion_rate", 0) < 50:
            summary["recommendations"].append(
                f"Improve email discovery for {analysis['city']} - only "
                f"{analysis.get('email_completion_rate', 0):.1f}% coverage"
            )
        if analysis.get("phone_completion_rate", 0) < 50:
            summary["recommendations"].append(
                f"Improve phone discovery for {analysis['city']} - only "
                f"{analysis.get('phone_completion_rate', 0):.1f}% coverage"
            )

    return summary


def main():
    """Main processing function."""
    print("=" * 70)
    print("ENHANCED PROPERTY PROCESSING PIPELINE")
    print("=" * 70)

    # Step 1: Load existing data
    print("\n🔄 Step 1: Loading existing processed data...")
    data = load_existing_data()

    if not data:
        print("❌ No processed data found. Please run the initial processing pipeline first.")
        return

    # Step 2: Check API status
    print("\n🔄 Step 2: Checking API and service status...")
    api_status = check_api_status()
    print(f"   Google Sheets: {'✅' if api_status['google_sheets'] else '❌'}")
    print(f"   Hunter.io: {'✅' if api_status['hunter_io'] else '❌'}")
    print(f"   ZeroBounce: {'✅' if api_status['zerobounce'] else '❌'}")
    print(f"   Gmail: {'✅' if api_status['gmail'] else '❌'}")

    # Step 3: Analyze data quality
    print("\n🔄 Step 3: Analyzing data quality...")
    analyses = []
    export_results = {}

    for city_name, df in data.items():
        print(f"\n   Analyzing {city_name}...")
        analysis = analyze_data_quality(df, city_name)
        analyses.append(analysis)

        print(f"   • Total records: {analysis['total_records']}")
        if "email_completion_rate" in analysis:
            print(f"   • Email completion: {analysis['email_completion_rate']:.1f}%")
        if "phone_completion_rate" in analysis:
            print(f"   • Phone completion: {analysis['phone_completion_rate']:.1f}%")
        if "avg_quality_score" in analysis:
            print(f"   • Average quality score: {analysis['avg_quality_score']:.1f}")

        # Step 4: Export to Google Sheets
        print(f"\n🔄 Step 4: Exporting {city_name} to Google Sheets...")
        export_success = export_to_google_sheets(df, f"{city_name}_properties", analysis)
        export_results[city_name] = export_success

    # Step 5: Generate comprehensive summary
    print("\n🔄 Step 5: Generating processing summary...")
    summary = generate_processing_summary(data, analyses, api_status, export_results)

    # Save summary to file
    summary_file = (
        f"outputs/enhanced_processing_summary_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"
    )
    Path("outputs").mkdir(exist_ok=True)

    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"✅ Summary saved to: {summary_file}")

    # Step 6: Generate text report
    print("\n🔄 Step 6: Generating text report...")

    report_lines = [
        "=" * 70,
        "ENHANCED PROCESSING RESULTS SUMMARY",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "=" * 70,
        "",
        "PROCESSING OVERVIEW:",
        f"• Cities processed: {summary['total_cities_processed']}",
        f"• Total records: {summary['total_records_processed']}",
        "",
        "API STATUS:",
        f"• Google Sheets: {'✅ Configured' if api_status['google_sheets'] else '❌ Not configured'}",
        f"• Hunter.io: {'✅ Configured' if api_status['hunter_io'] else '❌ Not configured'}",
        f"• ZeroBounce: {'✅ Configured' if api_status['zerobounce'] else '❌ Not configured'}",
        f"• Gmail: {'✅ Configured' if api_status['gmail'] else '❌ Not configured'}",
        "",
        "EXPORT RESULTS:",
    ]

    for city, success in export_results.items():
        report_lines.append(f"• {city}: {'✅ Success' if success else '❌ Failed'}")

    report_lines.extend(
        [
            "",
            "DATA QUALITY BY CITY:",
        ]
    )

    for analysis in analyses:
        report_lines.extend(
            [
                f"\n{analysis['city'].upper()}:",
                f"• Records: {analysis['total_records']}",
                f"• Email completion: {analysis.get('email_completion_rate', 0):.1f}%",
                f"• Phone completion: {analysis.get('phone_completion_rate', 0):.1f}%",
                f"• Quality score: {analysis.get('avg_quality_score', 0):.1f}",
            ]
        )

    if summary["recommendations"]:
        report_lines.extend(
            [
                "",
                "RECOMMENDATIONS:",
            ]
        )
        for rec in summary["recommendations"]:
            report_lines.append(f"• {rec}")

    report_lines.extend(["", "=" * 70, "END OF REPORT", "=" * 70])

    # Save text report
    report_file = (
        f"outputs/enhanced_processing_report_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"
    )

    with open(report_file, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    print(f"✅ Report saved to: {report_file}")

    # Print summary to console
    print("\n" + "=" * 70)
    print("PROCESSING COMPLETED SUCCESSFULLY")
    print("=" * 70)
    print(f"Cities processed: {summary['total_cities_processed']}")
    print(f"Total records: {summary['total_records_processed']}")
    print(
        f"Google Sheets exports: {sum(1 for success in export_results.values() if success)}/{len(export_results)}"
    )

    if summary["recommendations"]:
        print(f"\nNext steps: {len(summary['recommendations'])} recommendations generated")
        for i, rec in enumerate(summary["recommendations"][:3], 1):
            print(f"  {i}. {rec}")
        if len(summary["recommendations"]) > 3:
            print(f"  ... and {len(summary['recommendations']) - 3} more (see report)")


if __name__ == "__main__":
    main()
