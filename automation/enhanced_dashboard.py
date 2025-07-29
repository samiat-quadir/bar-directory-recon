"""
Enhanced Dashboard Manager with Jinja2 Templates

This refactored version replaces string concatenation with proper templating,
adds chart support, and includes WebSocket stubs for future real-time updates.
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from jinja2 import Environment, FileSystemLoader, select_autoescape

    JINJA2_AVAILABLE = True
except ImportError:
    JINJA2_AVAILABLE = False

try:
    from loguru import logger  # type: ignore
except ImportError:
    logger = logging.getLogger(__name__)


class EnhancedDashboardManager:
    """
    Enhanced dashboard manager with template-based HTML generation,
    chart support, and improved data visualization.
    """

    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config
        self.local_config = config.get("local_html", {})
        self.google_config = config.get("google_sheets", {})
        self.status_file = Path("logs/automation/status.json")
        self.templates_dir = Path(__file__).parent / "templates"

        # Initialize Jinja2 environment
        if JINJA2_AVAILABLE:
            self.jinja_env: Optional[Environment] = Environment(
                loader=FileSystemLoader(self.templates_dir), autoescape=select_autoescape(["html", "xml"])
            )
        else:
            logger.warning("Jinja2 not available, falling back to string concatenation")
            self.jinja_env = None

        self.ensure_status_file()

    def ensure_status_file(self) -> None:
        """Ensure status file exists with initial structure."""
        if not self.status_file.exists():
            self.status_file.parent.mkdir(parents=True, exist_ok=True)
            initial_status = {
                "last_updated": datetime.now().isoformat(),
                "sites": {},
                "global_stats": {"total_runs": 0, "successful_runs": 0, "failed_runs": 0},
                "history": [],
            }
            with open(self.status_file, "w") as f:
                json.dump(initial_status, f, indent=2)

    def load_status(self) -> Dict[str, Any]:
        """Load current status from file."""
        try:
            with open(self.status_file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Error loading status: {e}")
            return self._get_default_status()

    def _get_default_status(self) -> Dict[str, Any]:
        """Get default status structure."""
        return {
            "last_updated": datetime.now().isoformat(),
            "sites": {},
            "global_stats": {"total_runs": 0, "successful_runs": 0, "failed_runs": 0},
            "history": [],
        }

    def update_site_status(
        self, site_name: str, status: str, run_time: Optional[float] = None, error_message: Optional[str] = None
    ) -> None:
        """Update status for a specific site."""
        current_status = self.load_status()

        # Update site-specific data
        if site_name not in current_status["sites"]:
            current_status["sites"][site_name] = {}

        current_status["sites"][site_name].update(
            {
                "status": status,
                "last_updated": datetime.now().isoformat(),
                "last_run_time": f"{run_time:.2f}s" if run_time else None,
                "error_message": error_message,
            }
        )

        # Update global stats
        current_status["global_stats"]["total_runs"] += 1
        if status == "success":
            current_status["global_stats"]["successful_runs"] += 1
        elif status == "failed":
            current_status["global_stats"]["failed_runs"] += 1

        # Add to history (keep last 24 hours)
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "site": site_name,
            "status": status,
            "run_time": run_time,
        }
        current_status["history"].append(history_entry)

        # Cleanup old history entries
        cutoff_time = datetime.now() - timedelta(hours=24)
        current_status["history"] = [
            entry for entry in current_status["history"] if datetime.fromisoformat(entry["timestamp"]) > cutoff_time
        ]

        # Save updated status
        current_status["last_updated"] = datetime.now().isoformat()
        with open(self.status_file, "w") as f:
            json.dump(current_status, f, indent=2)

        logger.info(f"Updated status for {site_name}: {status}")

    def generate_dashboard(self) -> None:
        """Generate dashboard based on configuration."""
        try:
            if self.local_config.get("enabled", True):
                self._generate_html_dashboard()

            if self.google_config.get("enabled", False):
                self._update_google_sheets()

        except Exception as e:
            logger.error(f"Failed to generate dashboard: {e}")

    def _generate_html_dashboard(self) -> None:
        """Generate local HTML dashboard using Jinja2 templates."""
        status = self.load_status()
        output_path = Path(self.local_config.get("output_path", "output/dashboard.html"))
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if self.jinja_env:
            html_content = self._create_html_content_jinja2(status)
        else:
            html_content = self._create_html_content_fallback(status)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        logger.info(f"HTML dashboard generated: {output_path}")

    def _create_html_content_jinja2(self, status: Dict[str, Any]) -> str:
        """Create HTML content using Jinja2 templates."""
        if not self.jinja_env:
            raise RuntimeError("Jinja2 environment not available")

        template = self.jinja_env.get_template("dashboard.html")

        # Prepare data for template
        template_data = self._prepare_template_data(status)

        return template.render(**template_data)

    def _prepare_template_data(self, status: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for template rendering."""
        global_stats = status.get("global_stats", {})
        sites = status.get("sites", {})
        history = status.get("history", [])

        # Calculate success rate
        total_runs = global_stats.get("total_runs", 0)
        successful_runs = global_stats.get("successful_runs", 0)
        success_rate = (successful_runs / total_runs * 100) if total_runs > 0 else 0

        # Determine success rate class for styling
        if success_rate >= 90:
            success_rate_class = "success"
        elif success_rate < 70:
            success_rate_class = "danger"
        else:
            success_rate_class = "warning"

        # Process site data for template
        processed_sites = {}
        for site_name, site_data in sites.items():
            site_status = site_data.get("status", "unknown")

            # Add visual indicators
            status_colors = {"success": "#28a745", "failed": "#dc3545", "running": "#ffc107", "unknown": "#6c757d"}

            status_icons = {"success": "✅", "failed": "❌", "running": "🔄", "unknown": "❓"}

            processed_sites[site_name] = {
                **site_data,
                "color": status_colors.get(site_status, "#6c757d"),
                "icon": status_icons.get(site_status, "❓"),
            }

        # Generate chart data
        chart_data = self._generate_chart_data(history) if history else None

        return {
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "global_stats": global_stats,
            "success_rate": success_rate,
            "success_rate_class": success_rate_class,
            "sites": processed_sites,
            "chart_data": chart_data,
            "monitoring": self.config.get("monitoring", {}),
            "notifications": self.config.get("notifications", {}),
        }

    def _generate_chart_data(self, history: List[Dict[str, Any]]) -> Optional[Dict[str, List[Any]]]:
        """Generate data for Chart.js visualization."""
        if not history:
            return None

        # Group history by hour for the last 24 hours
        hourly_data = {}
        now = datetime.now()

        for i in range(24):
            hour_start = now - timedelta(hours=i + 1)
            hour_key = hour_start.strftime("%H:00")
            hourly_data[hour_key] = {"total": 0, "success": 0}

        # Process history entries
        for entry in history:
            entry_time = datetime.fromisoformat(entry["timestamp"])
            hour_key = entry_time.strftime("%H:00")

            if hour_key in hourly_data:
                hourly_data[hour_key]["total"] += 1
                if entry["status"] == "success":
                    hourly_data[hour_key]["success"] += 1

        # Convert to chart format
        labels = sorted(hourly_data.keys())
        total_runs = [hourly_data[label]["total"] for label in labels]
        success_rates = [
            (hourly_data[label]["success"] / hourly_data[label]["total"] * 100)
            if hourly_data[label]["total"] > 0
            else 0
            for label in labels
        ]

        return {"labels": labels, "total_runs": total_runs, "success_rates": success_rates}

    def _create_html_content_fallback(self, status: Dict[str, Any]) -> str:
        """Fallback HTML generation without Jinja2."""
        global_stats = status.get("global_stats", {})
        sites = status.get("sites", {})

        # Basic HTML structure (simplified)
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Universal Runner Dashboard</title>
            <meta charset="UTF-8">
            <meta http-equiv="refresh" content="30">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #f8f9fa; padding: 20px; border-radius: 5px; }}
                .stats {{ display: flex; gap: 20px; margin: 20px 0; }}
                .stat-card {{ background: white; border: 1px solid #ddd; padding: 15px; border-radius: 5px; }}
                .sites {{ margin: 20px 0; }}
                .site-card {{ border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Universal Runner Dashboard</h1>
                <p>Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            </div>

            <div class="stats">
                <div class="stat-card">
                    <h3>{global_stats.get("total_runs", 0)}</h3>
                    <p>Total Runs</p>
                </div>
                <div class="stat-card">
                    <h3>{global_stats.get("successful_runs", 0)}</h3>
                    <p>Successful</p>
                </div>
                <div class="stat-card">
                    <h3>{global_stats.get("failed_runs", 0)}</h3>
                    <p>Failed</p>
                </div>
            </div>

            <div class="sites">
                <h2>Sites Status</h2>
        """

        for site_name, site_data in sites.items():
            html += f"""
                <div class="site-card">
                    <h3>{site_name}</h3>
                    <p>Status: {site_data.get("status", "unknown")}</p>
                    <p>Last Updated: {site_data.get("last_updated", "Never")}</p>
                </div>
            """

        html += """
            </div>
        </body>
        </html>
        """

        return html

    def _update_google_sheets(self) -> None:
        """Update Google Sheets dashboard (placeholder for future implementation)."""
        logger.info("Google Sheets integration not yet implemented")
        # TODO: Implement Google Sheets API integration
        pass


# Backward compatibility function
def create_dashboard_manager(config: Dict[str, Any]) -> EnhancedDashboardManager:
    """Create dashboard manager instance."""
    return EnhancedDashboardManager(config)
