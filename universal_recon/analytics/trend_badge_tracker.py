# === analytics/trend_badge_tracker.py ===

import argparse
import json
from pathlib import Path


def regenerate_site_score_trend(
    site: str, archive_dir="output/archive", output_dir="output/reports"
) -> str:
    archive = Path(archive_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    snapshots = sorted(archive.glob("schema_matrix_*.json"))
    trend_scores = {}

    for snap in snapshots:
        with snap.open("r", encoding="utf-8") as f:
            data = json.load(f)
        site_data = data.get("sites", {}).get(site, {})
        score = site_data.get("score_summary", {}).get("field_score")
        if score is not None:
            trend_scores.setdefault("field_score", []).append(round(score, 2))

    save_path = output_path / f"{site}_trend.json"
    with save_path.open("w", encoding="utf-8") as f:
        json.dump({"trend_scores": trend_scores}, f, indent=2)
    return str(save_path)


def run_analysis(config: dict = None) -> dict:
    site = config.get("site_name", "unknown")
    output_dir = config.get("output_dir", "output/reports")

    root = Path(__file__).resolve().parent.parent
    trend_path = root / output_dir / f"{site}_trend.json"
    badge_path = root / "output" / "badge_matrix.json"

    result = {
        "plugin": "trend_badge_tracker",
        "site": site,
        "regressions": [],
        "status": "ok",
    }

    try:
        if not trend_path.exists():
            regenerate_site_score_trend(site=site)

        with trend_path.open("r", encoding="utf-8") as f:
            trend_data = json.load(f)
        with badge_path.open("r", encoding="utf-8") as f:
            badge_data = json.load(f)

        trend_scores = trend_data.get("trend_scores", {}).get("field_score", [])
        badge_overlay = badge_data.get("badge_overlay", {})

        for plugin, badge_counts in badge_overlay.items():
            critical_now = badge_counts.get("critical", 0)
            if len(trend_scores) >= 2:
                if trend_scores[-1] < trend_scores[-2] and critical_now > 0:
                    result["regressions"].append(
                        {
                            "plugin": plugin,
                            "old_score": trend_scores[-2],
                            "new_score": trend_scores[-1],
                            "critical_now": critical_now,
                        }
                    )

    except FileNotFoundError as e:
        result["status"] = "error"
        result["error"] = f"File not found: {e}"
    except json.JSONDecodeError as e:
        result["status"] = "error"
        result["error"] = f"JSON decoding failed: {e}"
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)

    return result


def print_summary(results: dict):
    print(f"\n📉 Badge Regression Report – {results.get('site')}")
    if results.get("status") != "ok":
        print("  ❌ Error:", results.get("error"))
        return
    regressions = results.get("regressions", [])
    if not regressions:
        print("  ✅ No regressions detected. Trend scores are stable.")
    else:
        for entry in regressions:
            print(
                f"  🔻 {entry['plugin']} dropped from {entry['old_score']} → {entry['new_score']} with 🔴 {entry['critical_now']} badge(s)"
            )
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", required=True)
    args = parser.parse_args()
    print_summary(run_analysis({"site_name": args.site}))
