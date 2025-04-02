import argparse
import os
from core.config_manager import ConfigManager
from core.orchestrator import ReconOrchestrator
from core.plugin_loader import load_plugins
from core.report_printer import print_reports
from core.retry import retry

from analytics.full_report_generator import generate_full_report

from utils.score_predictor import predict_scores
from validators.record_field_validator_v3 import validate_records


def console_logger(msg, level="INFO"):
    print(f"[{level}] {msg}")


def main():
    parser = argparse.ArgumentParser(description="Universal Recon Tool")
    parser.add_argument("--site", help="Site key to scrape (e.g., utah_bar)", default=None)
    parser.add_argument("--url", help="Custom URL to scrape", default=None)
    parser.add_argument("--strict", action="store_true", help="Enable strict record normalization")
    parser.add_argument("--dry-run", action="store_true", help="Run without saving or submitting")
    parser.add_argument("--run-plugin", help="Run a single plugin by name", default=None)
    parser.add_argument("--ml-score", action="store_true", help="Enable ML scoring fallback")
    parser.add_argument("--strict-schema", action="store_true", help="Run v3 validator in strict mode")
    parser.add_argument("--verbose-validation", action="store_true", help="Print badge-style errors")
    parser.add_argument("--recon-report", action="store_true", help="Print recon summary")
    parser.add_argument("--audit-report", action="store_true", help="Generate audit output")
    parser.add_argument("--audit-heatmap", action="store_true", help="Generate plugin/field heatmap")
    parser.add_argument("--trend-analysis", action="store_true", help="Track score/plugin drift across runs")
    parser.add_argument("--full-report", action="store_true", help="Generate single merged report")
    parser.add_argument("--run-mode", choices=["lite", "full"], default="full", help="Select plugin loading mode")
    args = parser.parse_args()

    config_path = os.path.join("configs", "defaults.json")
    cm = ConfigManager(config_path)

    # Apply CLI overrides
    cm.set("cli.strict", args.strict)
    cm.set("cli.dry_run", args.dry_run)
    cm.set("cli.run_plugin", args.run_plugin)
    cm.set("cli.ml_score", args.ml_score)
    cm.set("cli.strict_schema", args.strict_schema)
    cm.set("cli.verbose_validation", args.verbose_validation)
    cm.set("cli.recon_report", args.recon_report)
    cm.set("cli.audit_report", args.audit_report)
    cm.set("cli.audit_heatmap", args.audit_heatmap)
    cm.set("cli.trend_analysis", args.trend_analysis)
    cm.set("cli.full_report", args.full_report)
    cm.set("cli.run_mode", args.run_mode)

    # Orchestration
    orchestrator = ReconOrchestrator(cm, console_logger)

    try:
        # Select site & URL
        if args.site and args.url:
            clustered = orchestrator.run_recon(args.site, args.url)
        elif args.site:
            domain_cfg = os.path.join("configs", f"{args.site}.json")
            cm.merge_domain_config(domain_cfg)
            domain_url = cm.get("site.url")
            clustered = orchestrator.run_recon(args.site, domain_url)
        elif args.url:
            clustered = orchestrator.run_recon("custom", args.url)
        else:
            console_logger("No target provided", "ERROR")
            return

        # Flatten records
        all_fields = []
        for group in clustered:
            all_fields.extend(group.get("fields", []))

        # Optional: ML score
        if args.ml_score:
            all_fields = predict_scores(all_fields)

        # Schema validation
        validated = validate_records(
            all_fields,
            strict=args.strict_schema,
            verbose=args.verbose_validation
        )

        # Load and run plugins (analytics, etc.)
        plugins = load_plugins(args.run_mode)

        # Report generation and printing
        if args.full_report:
            full = generate_full_report(validated, args.site)
            print_reports(full, report_type="full", verbose=args.verbose_validation)
        else:
            print_reports(validated, report_type="modular", verbose=args.verbose_validation)

    finally:
        orchestrator.close()


if __name__ == "__main__":
    main()
