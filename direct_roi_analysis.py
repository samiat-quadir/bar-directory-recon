#!/usr/bin/env python3
"""
Direct ROI Analysis - Build Top-ROI list from coverage report
"""
import json
import pathlib
import subprocess
import sys


def analyze_coverage_and_roi():
    """Direct analysis using coverage report output"""
    print("🎯 DIRECT ROI ANALYSIS")
    print("=" * 40)
    
    # Parse the previous coverage output to get file-level data
    coverage_files = [
        {"file": "src/data_extractor.py", "statements": 272, "missed": 251, "coverage": 8},
        {"file": "src/data_hunter.py", "statements": 268, "missed": 230, "coverage": 14},
        {"file": "src/orchestrator.py", "statements": 277, "missed": 242, "coverage": 13},
        {"file": "src/config_loader.py", "statements": 120, "missed": 91, "coverage": 24},
        {"file": "src/property_validation.py", "statements": 286, "missed": 247, "coverage": 14},
        {"file": "src/pdf_processor.py", "statements": 220, "missed": 220, "coverage": 0},
        {"file": "src/property_enrichment.py", "statements": 211, "missed": 211, "coverage": 0},
        {"file": "src/pagination_manager.py", "statements": 204, "missed": 187, "coverage": 8},
        {"file": "src/ut_bar.py", "statements": 188, "missed": 188, "coverage": 0},
        {"file": "src/webdriver_manager.py", "statements": 177, "missed": 165, "coverage": 7},
        {"file": "src/notification_agent.py", "statements": 169, "missed": 169, "coverage": 0},
        {"file": "src/logger.py", "statements": 165, "missed": 134, "coverage": 19},
        {"file": "src/security_audit.py", "statements": 165, "missed": 165, "coverage": 0},
        {"file": "src/hallandale_pipeline.py", "statements": 162, "missed": 162, "coverage": 0},
        {"file": "src/unified_schema.py", "statements": 153, "missed": 110, "coverage": 28},
        {"file": "src/hallandale_pipeline_fixed.py", "statements": 140, "missed": 140, "coverage": 0},
        {"file": "src/refactored_scraping_orchestrator.py", "statements": 95, "missed": 95, "coverage": 0},
        {"file": "src/security_manager.py", "statements": 88, "missed": 23, "coverage": 74},
    ]
    
    # Get complexity data with radon
    try:
        result = subprocess.run(["radon", "cc", "-j", "src"], capture_output=True, text=True)
        complexity_data = json.loads(result.stdout) if result.stdout else {}
    except:
        complexity_data = {}
    
    # Calculate ROI for each file
    roi_candidates = []
    
    for file_data in coverage_files:
        filename = file_data["file"]
        gap = file_data["missed"]  # Uncovered lines
        total = file_data["statements"]
        
        # Calculate complexity score
        complexity = 0
        for cc_file, cc_data in complexity_data.items():
            if filename.endswith(pathlib.Path(cc_file).name) or cc_file.endswith(pathlib.Path(filename).name):
                # Weight by complexity rank
                rank_weights = {"A": 1, "B": 2, "C": 3, "D": 5, "E": 8, "F": 13}
                complexity = sum(rank_weights.get(item.get("rank", "A"), 1) for item in cc_data)
                break
        
        # ROI = gap × (1 + complexity) - prioritize high-impact files
        roi = gap * (1 + complexity)
        
        if gap > 0:  # Only files with uncovered lines
            roi_candidates.append({
                "file": filename,
                "roi": roi,
                "gap": gap,
                "complexity": complexity,
                "total": total,
                "covered": total - gap,
                "coverage_pct": file_data["coverage"]
            })
    
    # Sort by ROI (highest first)
    roi_candidates.sort(key=lambda x: -x["roi"])
    
    # Take top 10
    top_candidates = roi_candidates[:10]
    
    # Save results
    pathlib.Path("logs/nextwave/top_roi.json").write_text(
        json.dumps(top_candidates, indent=2), encoding="utf-8"
    )
    
    print("📊 TOP ROI TARGETS:")
    for i, cand in enumerate(top_candidates, 1):
        print(f"   {i:2d}. {pathlib.Path(cand['file']).name:<30} ROI:{cand['roi']:>6} Gap:{cand['gap']:>3} Comp:{cand['complexity']:>2}")
    
    print(f"\n✅ Generated {len(top_candidates)} ROI targets for testing")
    return top_candidates


def main():
    """Main execution"""
    try:
        candidates = analyze_coverage_and_roi()
        print(f"TOP_ROI_READY {len(candidates)}")
        return 0
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())