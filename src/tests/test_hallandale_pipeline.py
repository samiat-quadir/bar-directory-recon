from hallandale_pipeline import HallandalePipeline  # type: ignore


def test_pipeline_nonexistent_pdf(tmp_path) -> None:
    # Using a non-existent PDF should cause pipeline to fail early
    output_dir = tmp_path / "out"
    pipeline = HallandalePipeline(str(output_dir))
    results = pipeline.run_full_pipeline(str(tmp_path / "does_not_exist.pdf"))
    assert results["pipeline_status"] == "failed"
    assert any("PDF processing failed" in err for err in results.get("errors", []))
