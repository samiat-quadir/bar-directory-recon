import os
from hallandale_pipeline import HallandalePipeline  # type: ignore

def test_pipeline_success(tmp_path, monkeypatch):
    # Setup pipeline with temporary output directory
    output_dir = tmp_path / "out"
    pipeline = HallandalePipeline(str(output_dir))

    # Prepare dummy file paths
    dummy_pdf = str(tmp_path / "input.pdf")
    dummy_csv = str(tmp_path / "data.csv")
    dummy_enriched = str(tmp_path / "enriched.csv")
    dummy_excel = str(tmp_path / "report.xlsx")

    # Monkeypatch processing steps
    monkeypatch.setattr(pipeline.pdf_processor, "process_pdf", lambda path: {
        "status": "success",
        "properties_count": 5,
        "output_file": dummy_csv
    })
    monkeypatch.setattr(pipeline.enricher, "enrich_properties", lambda path: {
        "status": "success",
        "enriched_count": 5,
        "output_file": dummy_enriched
    })
    monkeypatch.setattr(pipeline.enricher, "generate_summary_report", lambda path: {
        "total_records_processed": 5,
        "records_with_emails": 2,
        "records_with_phones": 3,
        "priority_records": 1,
        "corporate_entities": 1,
        "individual_owners": 4,
        "average_data_quality_score": 92,
        "needs_manual_review": 1
    })
    monkeypatch.setattr(pipeline.validator, "validate_properties", lambda path: {"status": "success"})
    monkeypatch.setattr(pipeline, "_create_excel_export", lambda path: {
        "status": "success",
        "output_file": dummy_excel
    })

    # Run the pipeline
    results = pipeline.run_full_pipeline(dummy_pdf)

    # Assert successful pipeline run and steps
    assert results["pipeline_status"] == "success"
    assert "pdf_processing" in results["steps_completed"]
    assert "property_enrichment" in results["steps_completed"]
    assert "excel_export" in results["steps_completed"]

    # Check content of enrichment summary and excel result
    summary = results.get("enrichment_summary", {})
    assert summary.get("total_records_processed") == 5
    excel_res = results.get("excel_result", {})
    assert excel_res.get("output_file") == dummy_excel
