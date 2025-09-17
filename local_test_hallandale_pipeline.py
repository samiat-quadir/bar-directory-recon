#!/usr/bin/env python3
"""
Test script for the complete Hallandale property processing pipeline
"""

import sys
from pathlib import Path

import pandas as pd

# Add src to path and import modules
sys.path.append("src")
from pdf_processor import HallandalePropertyProcessor
from property_enrichment import PropertyEnrichment
from property_validation import PropertyValidation


def test_complete_pipeline():
    """Test the complete pipeline with sample data."""

    print("=" * 60)
    print("HALLANDALE PROPERTY PROCESSING PIPELINE TEST")
    print("=" * 60)

    # Step 1: Create sample data
    print("\nStep 1: Creating sample property data...")
    processor = HallandalePropertyProcessor()
    sample_data = processor._create_sample_data()

    # Add some corporate entities for testing
    sample_data[0]["owner_name"] = "Miami Properties LLC"
    sample_data[1]["owner_name"] = "Sunshine Investments Inc"
    sample_data[2]["owner_name"] = "Beachfront Holdings Corp"

    df = pd.DataFrame(sample_data)
    output_dir = Path("outputs/hallandale")
    output_dir.mkdir(parents=True, exist_ok=True)

    raw_file = output_dir / "hallandale_properties_raw.csv"
    df.to_csv(raw_file, index=False)
    print(f"✓ Created sample data: {len(sample_data)} properties")

    # Step 2: Enrich properties
    print("\nStep 2: Enriching property data...")
    enricher = PropertyEnrichment()
    enrichment_result = enricher.enrich_properties(str(raw_file))

    if enrichment_result["status"] == "success":
        print(
            f"✓ Enrichment completed: {enrichment_result['enriched_count']} properties"
        )

        # Generate summary
        summary = enricher.generate_summary_report(enrichment_result["output_file"])
        print("✓ Summary report generated")

        # Display key metrics
        print("\nKey Metrics:")
        print(f"  Total records: {summary.get('total_records_processed', 0)}")
        print(f"  Records with emails: {summary.get('records_with_emails', 0)}")
        print(f"  Records with phones: {summary.get('records_with_phones', 0)}")
        print(f"  Priority records: {summary.get('priority_records', 0)}")
        print(f"  Corporate entities: {summary.get('corporate_entities', 0)}")
        print(
            f"  Average quality score: {summary.get('average_data_quality_score', 0)}/100"
        )

    else:
        print(
            f"✗ Enrichment failed: {enrichment_result.get('message', 'Unknown error')}"
        )
        return

    # Step 3: Validate properties
    print("\nStep 3: Validating property data...")
    validator = PropertyValidation()
    validation_result = validator.validate_properties(enrichment_result["output_file"])

    if validation_result["status"] == "success":
        print("✓ Validation completed")
    else:
        print(
            f"✗ Validation failed: {validation_result.get('message', 'Unknown error')}"
        )

    # Step 4: Create Excel export
    print("\nStep 4: Creating Excel export...")
    try:
        enriched_df = pd.read_csv(enrichment_result["output_file"])

        excel_file = output_dir / "hallandale_properties_complete.xlsx"
        with pd.ExcelWriter(excel_file, engine="openpyxl") as writer:
            # Main data sheet
            enriched_df.to_excel(writer, sheet_name="All Properties", index=False)

            # Priority properties
            priority_df = enriched_df[enriched_df["priority_flag"] == True]
            priority_df.to_excel(writer, sheet_name="Priority Properties", index=False)

            # Corporate entities
            corporate_df = enriched_df[enriched_df["is_corporate"] == True]
            corporate_df.to_excel(writer, sheet_name="Corporate Entities", index=False)

            # Missing contact info
            missing_contact = enriched_df[
                (enriched_df["owner_email"].isna() | (enriched_df["owner_email"] == ""))
                & (
                    enriched_df["owner_phone"].isna()
                    | (enriched_df["owner_phone"] == "")
                )
            ]
            missing_contact.to_excel(
                writer, sheet_name="Missing Contact Info", index=False
            )

        print(f"✓ Excel file created: {excel_file}")
        print(f"  - All Properties: {len(enriched_df)} records")
        print(f"  - Priority Properties: {len(priority_df)} records")
        print(f"  - Corporate Entities: {len(corporate_df)} records")
        print(f"  - Missing Contact Info: {len(missing_contact)} records")

    except Exception as e:
        print(f"✗ Excel export failed: {e}")

    # Step 5: List all output files
    print("\nStep 5: Output files created:")
    for file_path in output_dir.rglob("*"):
        if file_path.is_file():
            print(f"  - {file_path.relative_to(output_dir)}")

    print("\n" + "=" * 60)
    print("PIPELINE TEST COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print("\nResults summary:")
    print(f"  📁 Output directory: {output_dir}")
    print(f"  📊 Total properties processed: {len(sample_data)}")
    print(f"  📧 Records with emails: {summary.get('records_with_emails', 0)}")
    print(f"  📞 Records with phones: {summary.get('records_with_phones', 0)}")
    print(f"  ⚠️  Priority records: {summary.get('priority_records', 0)}")
    print(f"  🏢 Corporate entities: {summary.get('corporate_entities', 0)}")
    print(f"  🔍 Needs manual review: {summary.get('needs_manual_review', 0)}")


if __name__ == "__main__":
    test_complete_pipeline()
