"""
Dashboard Manager for Universal Project Runner
============================================

Manages status dashboards including local HTML generation and Google Sheets integration.
Provides real-time status updates and historical tracking.
"""


import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional


try:
    from loguru import logger
except ImportError:
    logger = logging.getLogger(__name__)


class DashboardManager:
    """
    Manages status dashboards and reporting.
    Handles local HTML and Google Sheets integration.
    """

    config: Dict[str, Any]
    local_config: Dict[str, Any]
    google_config: Dict[str, Any]
    status_file: Path

    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config
        self.local_config = config.get('local_html', {})
        self.google_config = config.get('google_sheets', {})
        self.status_file = Path('logs/automation/status.json')
        self.ensure_status_file()

    def ensure_status_file(self) -> None:
        """Ensure status file exists with initial structure."""
        if not self.status_file.exists():
            self.status_file.parent.mkdir(parents=True, exist_ok=True)
            initial_status = {
                'last_updated': datetime.now().isoformat(),
                'sites': {},
                'global_stats': {
                    'total_runs': 0,
                    'successful_runs': 0,
                    'failed_runs': 0,
                    'last_run': datetime.now().isoformat()
                }
            }
            with open(self.status_file, 'w') as f:
                json.dump(initial_status, f, indent=2)

    def load_status(self) -> Dict[str, Any]:
        """Load current status from file."""
        try:
            with open(self.status_file, 'r') as f:
                data = json.load(f)
                # Ensure last_run is always a string
                if 'global_stats' in data and 'last_run' in data['global_stats']:
                    if not isinstance(data['global_stats']['last_run'], str):
                        data['global_stats']['last_run'] = str(data['global_stats']['last_run'])
                return data
        except Exception as e:
            logger.error(f"Failed to load status: {e}")
            return {}


    def save_status(self, status: Dict[str, Any]) -> None:
        """Save status to file."""
        try:
            status['last_updated'] = datetime.now().isoformat()
            if 'global_stats' in status:
                # Always store last_run as string
                status['global_stats']['last_run'] = str(status['global_stats'].get('last_run', datetime.now().isoformat()))
            with open(self.status_file, 'w') as f:
                json.dump(status, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save status: {e}")

    def health_check(self) -> bool:
        """Perform a health check for dashboard dependencies and folders."""
        ok = True
        if not self.status_file.parent.exists():
            logger.error(f"Dashboard log folder missing: {self.status_file.parent}")
            ok = False
        if not self.status_file.exists():
            logger.warning(f"Dashboard status file missing: {self.status_file}")
            ok = False
        return ok
    
    def update_site_status(self, site: str, status: str, details: Optional[Dict[str, Any]] = None) -> None:
        """
        Update status for a specific site.
        Args:
            site: The site name.
            status: Status string (e.g., 'success', 'failed').
            details: Optional details dict.
        """
        current_status = self.load_status()
        if 'sites' not in current_status:
            current_status['sites'] = {}
        current_status['sites'][site] = {
            'status': status,
            'last_updated': datetime.now().isoformat(),
            'details': details or {}
        }
        # Update global stats
        if 'global_stats' not in current_status:
            current_status['global_stats'] = {
                'total_runs': 0,
                'successful_runs': 0,
                'failed_runs': 0,
                'last_run': datetime.now().isoformat()
            }
        current_status['global_stats']['total_runs'] += 1
        current_status['global_stats']['last_run'] = datetime.now().isoformat()
        if status == 'success':
            current_status['global_stats']['successful_runs'] += 1
        elif status == 'failed':
            current_status['global_stats']['failed_runs'] += 1
        self.save_status(current_status)
        logger.info(f"Updated status for {site}: {status}")
    
    def generate_dashboard(self) -> None:
        """
        Generate dashboard in all configured formats (HTML, Google Sheets).
        """
        try:
            if self.local_config.get('enabled', True):
                self._generate_html_dashboard()
            if self.google_config.get('enabled', False):
                self._update_google_sheets()
            logger.info("Dashboard generated successfully")
        except Exception as e:
            logger.error(f"Failed to generate dashboard: {e}")
    
    def _generate_html_dashboard(self) -> None:
        """Generate local HTML dashboard."""
        status = self.load_status()
        output_path = Path(self.local_config.get('output_path', 'output/dashboard.html'))
        output_path.parent.mkdir(parents=True, exist_ok=True)
        html_content = self._create_html_content(status)
        with open(output_path, 'w') as f:
            f.write(html_content)
        logger.info(f"HTML dashboard generated: {output_path}")
    
    def _create_html_content(self, status: Dict[str, Any]) -> str:
        """Create HTML content for dashboard."""
        global_stats = status.get('global_stats', {})
        sites = status.get('sites', {})
        
        # Calculate success rate
        total_runs = global_stats.get('total_runs', 0)
        successful_runs = global_stats.get('successful_runs', 0)
        success_rate = (successful_runs / total_runs * 100) if total_runs > 0 else 0
        if success_rate >= 90:
            success_rate_class = 'success'
        elif success_rate < 70:
            success_rate_class = 'danger'
        else:
            success_rate_class = 'primary'
        
        # Generate site status cards
        site_cards = []
        for site_name, site_data in sites.items():
            site_status = site_data.get('status', 'unknown')
            last_updated = site_data.get('last_updated', 'Never')
            
            status_color = {
                'success': '#28a745',
                'failed': '#dc3545',
                'running': '#ffc107',
                'unknown': '#6c757d'
            }.get(site_status, '#6c757d')
            
            status_icon = {
                'success': '✅',
                'failed': '❌',
                'running': '🔄',
                'unknown': '❓'
            }.get(site_status, '❓')
            
            site_cards.append(f"""
                <div class="site-card">
                    <div class="site-header">
                        <span class="site-icon">{status_icon}</span>
                        <h3>{site_name}</h3>
                        <span class="status-badge" style="background-color: {status_color}">
                            {site_status.title()}
                        </span>
                    </div>
                    <div class="site-details">
                        <p><strong>Last Updated:</strong> {last_updated}</p>
                    </div>
                </div>
            """)
        
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Universal Runner Dashboard</title>
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background-color: #f5f5f5;
                    color: #333;
                    line-height: 1.6;
                }}
                
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                
                .header {{
                    text-align: center;
                    margin-bottom: 40px;
                }}
                
                .header h1 {{
                    color: #2c3e50;
                    font-size: 2.5rem;
                    margin-bottom: 10px;
                }}
                
                .header p {{
                    color: #7f8c8d;
                    font-size: 1.1rem;
                }}
                
                .stats-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 20px;
                    margin-bottom: 40px;
                }}
                
                .stat-card {{
                    background: white;
                    border-radius: 8px;
                    padding: 20px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    text-align: center;
                }}
                
                .stat-card h3 {{
                    color: #2c3e50;
                    margin-bottom: 10px;
                }}
                
                .stat-value {{
                    font-size: 2rem;
                    font-weight: bold;
                    margin-bottom: 5px;
                }}
                
                .success {{ color: #28a745; }}
                .danger {{ color: #dc3545; }}
                .primary {{ color: #007bff; }}
                
                .sites-section {{
                    margin-top: 40px;
                }}
                
                .sites-section h2 {{
                    color: #2c3e50;
                    margin-bottom: 20px;
                    border-bottom: 2px solid #3498db;
                    padding-bottom: 10px;
                }}
                
                .sites-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                    gap: 20px;
                }}
                
                .site-card {{
                    background: white;
                    border-radius: 8px;
                    padding: 20px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    transition: transform 0.2s;
                }}
                
                .site-card:hover {{
                    transform: translateY(-2px);
                    box-shadow: 0 4px 8px rgba(0,0,0,0.15);
                }}
                
                .site-header {{
                    display: flex;
                    align-items: center;
                    margin-bottom: 10px;
                }}
                
                .site-icon {{
                    font-size: 1.5rem;
                    margin-right: 10px;
                }}
                
                .site-header h3 {{
                    flex: 1;
                    color: #2c3e50;
                }}
                
                .status-badge {{
                    color: white;
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-size: 0.8rem;
                    font-weight: bold;
                }}
                
                .site-details {{
                    color: #7f8c8d;
                    font-size: 0.9rem;
                }}
                
                .footer {{
                    text-align: center;
                    margin-top: 40px;
                    padding: 20px;
                    color: #7f8c8d;
                    border-top: 1px solid #ecf0f1;
                }}
                
                .refresh-info {{
                    background: #e8f4ff;
                    border: 1px solid #bee5eb;
                    border-radius: 4px;
                    padding: 10px;
                    margin-bottom: 20px;
                    text-align: center;
                    color: #0c5460;
                }}
                
                @media (max-width: 768px) {{
                    .container {{
                        padding: 10px;
                    }}
                    
                    .header h1 {{
                        font-size: 2rem;
                    }}
                    
                    .stats-grid,
                    .sites-grid {{
                        grid-template-columns: 1fr;
                    }}
                }}
            </style>
            <script>
                // Auto-refresh every 5 minutes
                setTimeout(function(){{
                    window.location.reload();
                }}, 300000);
                
                // Add current time
                window.onload = function() {{
                    document.getElementById('currentTime').textContent = new Date().toLocaleString();
                }};
            </script>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔍 Universal Runner Dashboard</h1>
                    <p>Bar Directory Reconnaissance - Automation Status</p>
                </div>
                
                <div class="refresh-info">
                    📅 Last Updated: {status.get('last_updated', 'Unknown')} | 
                    🕐 Current Time: <span id="currentTime"></span> |
                    🔄 Auto-refresh: 5 minutes
                </div>
                
                <div class="stats-grid">
                    <div class="stat-card">
                        <h3>Total Runs</h3>
                        <div class="stat-value primary">{total_runs}</div>
                    </div>
                    
                    <div class="stat-card">
                        <h3>Successful Runs</h3>
                        <div class="stat-value success">{successful_runs}</div>
                    </div>
                    
                    <div class="stat-card">
                        <h3>Failed Runs</h3>
                        <div class="stat-value danger">{global_stats.get('failed_runs', 0)}</div>
                    </div>
                    
                    <div class="stat-card">
                        <h3>Success Rate</h3>
                        <div class="stat-value {success_rate_class}">
                            {success_rate:.1f}%
                        </div>
                    </div>
                </div>
                
                <div class="sites-section">
                    <h2>🌐 Site Status</h2>
                    <div class="sites-grid">
                        {''.join(site_cards) if site_cards else '<p>No sites configured yet.</p>'}
                    </div>
                </div>
                
                <div class="footer">
                    <p>Generated by Universal Runner Dashboard Manager</p>
                    <p>📊 Real-time monitoring for bar directory reconnaissance automation</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _update_google_sheets(self) -> None:
        """Update Google Sheets dashboard (stub)."""
        if not self.google_config.get('enabled'):
            return
        try:
            # This would integrate with Google Sheets API
            # For now, we'll log that it's not implemented
            logger.info("Google Sheets integration not yet implemented")
            # Future implementation would:
            # 1. Authenticate with Google Sheets API
            # 2. Update configured spreadsheet with current status
            # 3. Create charts and visualizations
        except Exception as e:
            logger.error(f"Failed to update Google Sheets: {e}")
    
    def get_stats_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics for notifications.
        Returns:
            Dictionary with total_runs, successful_runs, failed_runs, success_rate, sites_processed, files_processed.
        """
        status = self.load_status()
        global_stats = status.get('global_stats', {})
        total_runs = global_stats.get('total_runs', 0)
        successful_runs = global_stats.get('successful_runs', 0)
        return {
            'total_runs': total_runs,
            'successful_runs': successful_runs,
            'failed_runs': global_stats.get('failed_runs', 0),
            'success_rate': (successful_runs / total_runs * 100) if total_runs > 0 else 0,
            'sites_processed': len(status.get('sites', {})),
            'files_processed': 0  # Would be tracked separately
        }
