# === validators/run_phase_21b_analysis.py ===

import json
import os

ARCHIVE_PATH = "output/archive/"
LATEST_PATH = "output/schema_matrix.json"
REGRESSION_THRESHOLD = 5.0


def load_matrix(path):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception as e:
        print(f"[!] Failed to load {path}: {e}")
        return {}




def compare_scores(latest, previous):
    regressions = []

    latest_sites = latest.get("sites", {})
    prev_sites = previous.get("sites", {})


        drift = None
        if new_score is not None and old_score is not None:
            drift = round(new_score - old_score, 2)

        regress = drift is not None and drift < -REGRESSION_THRESHOLD
        anomaly_spike = new_anomalies > old_anomalies

        if regress or anomaly_spike:
            regressions.append(
                {
                    "site": site,
                    "score_drift": drift,
                    "old_score": old_score,
                    "new_score": new_score,
                    "anomaly_spike": anomaly_spike,
                    "old_anomalies": old_anomalies,
                    "new_anomalies": new_anomalies,
                }
            )

    return regressions


def print_summary(regressions):
    if not regressions:
        print("✅ No major regressions detected.")
        return

    print("⚠️  Detected potential issues:\n")
    for r in regressions:
        print(
            f"- {r['site']}: score dropped {r['score_drift']} "
            f"({r['old_score']} → {r['new_score']})"
            + (" + anomaly spike" if r["anomaly_spike"] else "")
        )


def main():
    print("📊 Phase 21b Sanity Checker")
    latest_path = LATEST_PATH
    previous_path = get_latest_snapshot_path()

    if not previous_path or not os.path.exists(latest_path):
        print("[!] Missing required matrix files.")
        exit(1)

    latest = load_matrix(latest_path)
    previous = load_matrix(previous_path)

    regressions = compare_scores(latest, previous)
    print_summary(regressions)

    if regressions:
        exit(1)
    else:
        exit(0)



if __name__ == "__main__":
    main()
