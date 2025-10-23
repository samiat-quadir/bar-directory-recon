"""Smoke test for the CLI demo pipeline."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path


def _run_stage(stage: str, repo_root: Path, *args: str) -> dict:
    cmd = ["python", "scripts/bdr.py", stage, *args]
    completed = subprocess.run(cmd, cwd=repo_root, capture_output=True, text=True)
    if completed.returncode != 0:
        raise AssertionError(
            f"Stage {stage} failed with code {completed.returncode}: {completed.stderr or completed.stdout}"
        )
    return json.loads(completed.stdout.strip())


def test_demo_pipeline(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    demo_src = repo_root / "examples" / "demo"
    work_dir = tmp_path / "demo"
    shutil.copytree(demo_src, work_dir)

    ingest_out = work_dir / "work" / "ingested.json"
    normalize_out = work_dir / "work" / "normalized.json"
    validate_out = work_dir / "work" / "validation.json"
    score_out = work_dir / "work" / "score.json"
    report_json = work_dir / "output" / "report.json"
    report_md = work_dir / "output" / "report.md"

    ingest_out.parent.mkdir(parents=True, exist_ok=True)
    report_json.parent.mkdir(parents=True, exist_ok=True)

    input_path = work_dir / "input" / "records.json"
    _run_stage("ingest", repo_root, "-i", str(input_path), "-o", str(ingest_out))
    _run_stage("normalize", repo_root, "-i", str(ingest_out), "-o", str(normalize_out))
    _run_stage("validate", repo_root, "-i", str(normalize_out), "-o", str(validate_out))
    _run_stage("score", repo_root, "-i", str(validate_out), "-o", str(score_out))
    _run_stage(
        "report",
        repo_root,
        "-i",
        str(score_out),
        "-o",
        str(report_json),
        "--markdown",
        str(report_md),
    )

    report = json.loads(report_json.read_text(encoding="utf-8"))
    assert report["records"] == 10
    assert report["errors"] == 0
    assert 0 <= report["score"] <= 100
    assert report_md.exists()
