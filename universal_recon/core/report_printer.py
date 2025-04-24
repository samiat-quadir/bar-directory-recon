# universal_recon/core/report_printer.py

def print_summary(summary):
    print("\n📝 Recon Summary Report")
    print(f"Total Records: {summary.get('total_records', 0)}")

def print_audit(audit):
    print("\n🧾 Audit Summary")
    for key, value in audit.items():
        print(f"  {key}: {value}")

def print_trend(trend):
    print("\n📈 Trend Analysis")
    print(f"  Score Trend: {trend.get('score_trend', 'None')}")

def print_health(health):
    print("\n🏥 Health Flags")
    for key, value in health.items():
        print(f"  {key}: {value}")
