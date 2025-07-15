#!/usr/bin/env python3
"""
Universal Project Runner - Phase 3 Automation Initiative
=========================================================

A comprehensive automation system for the bar-directory-recon project that:
- Schedules core scripts (scraping, validation, export) for daily/weekly runs
- Monitors for new data/list files in input/ and auto-processes them
- Sends error/success notifications to Discord or Email
- Maintains a rolling status dashboard in Google Sheets
- Supports headless (unattended) operation with comprehensive logging

Usage:
    python automation/universal_runner.py --mode schedule --frequency daily
    python automation/universal_runner.py --mode watch --input-dir input/
    python automation/universal_runner.py --mode pipeline --site example_bar
    python automation/universal_runner.py --mode status --dashboard
"""


import argparse
import asyncio
import json
import logging
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional, Set
import subprocess
import yaml  # type: ignore
import fnmatch

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(PROJECT_ROOT / 'logs' / 'automation' / 'universal_runner.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Import List Discovery Agent
try:
    from list_discovery.agent import ListDiscoveryAgent
    LIST_DISCOVERY_AVAILABLE = True
except ImportError:
    logger.warning("List Discovery Agent not available - web monitoring disabled")
    LIST_DISCOVERY_AVAILABLE = False

# Import automation components
try:
    from automation.notifier import NotificationManager
    from automation.dashboard import DashboardManager
    from automation.pipeline_executor import PipelineExecutor
except ImportError as e:
    logger.error(f"Failed to import automation components: {e}")
    sys.exit(1)

# Import scheduling and monitoring - we'll create simple implementations
try:
    import schedule  # type: ignore
    _schedule_module = schedule
except ImportError:
    # Simple fallback if schedule not installed
    class _schedule_module:
        class every:
            @staticmethod
            def day() -> "_schedule_module":
                return _schedule_module()
            @staticmethod
            def hour() -> "_schedule_module":
                return _schedule_module()
            @staticmethod
            def week() -> "_schedule_module":
                return _schedule_module()
            @staticmethod
            def sunday() -> "_schedule_module":
                return _schedule_module()
            @staticmethod
            def monday() -> "_schedule_module":
                return _schedule_module()
            @staticmethod
            def tuesday() -> "_schedule_module":
                return _schedule_module()
            @staticmethod
            def wednesday() -> "_schedule_module":
                return _schedule_module()
            @staticmethod
            def thursday() -> "_schedule_module":
                return _schedule_module()
class Observer:
    def __init__(self) -> None:
        self.is_alive_flag = False

    def schedule(self, handler, path: str, recursive: bool = False) -> None:
        pass

    def start(self) -> None:
        self.is_alive_flag = True

    def stop(self) -> None:
        self.is_alive_flag = False

    def join(self) -> None:
        pass

    def is_alive(self) -> bool:
        return self.is_alive_flag

class FileSystemEventHandler:
    def on_created(self, event) -> None:
        pass

    def on_modified(self, event) -> None:
        pass
        pass
    
    def start(self):
        self.is_alive_flag = True
    
    def stop(self):
        self.is_alive_flag = False
    
    def join(self):
        pass
    
    def is_alive(self):
        return self.is_alive_flag

class FileSystemEventHandler:
    def on_created(self, event):
        pass
    
    def on_modified(self, event):
        pass



class InputMonitor(FileSystemEventHandler):
    """Monitors input directories for new files and triggers processing"""
    runner: 'UniversalRunner'
    batch_timer: Optional[Any]
    pending_files: Set[Path]

    def __init__(self, runner_instance: 'UniversalRunner') -> None:
        self.runner = runner_instance
        self.batch_timer = None
        self.pending_files: Set[Path] = set()

    def on_created(self, event) -> None:
        if not getattr(event, "is_directory", False):
            self._handle_file_event(event.src_path)

    def on_modified(self, event: Any) -> None:
        if not getattr(event, "is_directory", False):
            self._handle_file_event(event.src_path)

    def _handle_file_event(self, file_path: str) -> None:
        """Handle new or modified files"""
        path_obj = Path(file_path)

        # Check if file matches monitoring patterns
        patterns = self.runner.config['monitoring']['file_patterns']
        if any(fnmatch.fnmatch(path_obj.name, pattern) for pattern in patterns):
            logger.info(f"Detected new file: {path_obj}")
            self.pending_files.add(path_obj)

            # Reset batch timer
            if self.batch_timer:
                self.batch_timer.cancel()

            batch_delay = self.runner.config['monitoring']['batch_delay']
            self.batch_timer = asyncio.get_event_loop().call_later(
                batch_delay, self._process_batch
            )

    def _process_batch(self) -> None:
        """Process all pending files as a batch"""
        if not self.pending_files:
            return

        logger.info(f"Processing batch of {len(self.pending_files)} files")

        for file_path in self.pending_files:
            try:
                self.runner.process_input_file(file_path)
            except Exception as e:
                logger.error(f"Failed to process {file_path}: {e}")

        self.pending_files.clear()
            
            # Reset batch timer

class UniversalRunner:
    """Main automation runner class for bar-directory-recon."""
    config_path: Path
    config: Dict[str, Any]
    notifier: Any
    dashboard: Any
    pipeline: Any
    input_monitor: InputMonitor
    observer: Optional[Any]
    is_running: bool
    list_discovery: Optional[Any]

    def __init__(self) -> None:
        # Initialize configuration
        self.config_path = Path('config/automation_config.yaml')
        self.config = self._load_config()
        # Health check for config folder
        if not self.config_path.parent.exists():
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created config directory: {self.config_path.parent}")
        # Initialize components with the config
        self.notifier = NotificationManager(self.config['notifications'])
        self.dashboard = DashboardManager(self.config['dashboard'])
        self.pipeline = PipelineExecutor(self.config['pipeline'])
        self.input_monitor = InputMonitor(self)
        self.observer = None
        self.is_running = False
        # Initialize List Discovery Agent if available
        self.list_discovery = None
        if LIST_DISCOVERY_AVAILABLE:
            try:
                self.list_discovery = ListDiscoveryAgent()
                logger.info("List Discovery Agent initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize List Discovery Agent: {e}")

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file, or return defaults if missing/corrupt."""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    loaded = yaml.safe_load(f)
                    if isinstance(loaded, dict):
                        return loaded
                    else:
                        logger.warning("Loaded config is not a dict, using default config.")
        except Exception as e:
            logger.warning(f"Failed to load config: {e}")
        # Return default configuration
        return {
            'schedules': {
                'scraping': {'frequency': 'daily', 'time': '02:00'},
                'validation': {'frequency': 'daily', 'time': '06:00'},
                'export': {'frequency': 'weekly', 'time': '23:00', 'day': 'sunday'},
                'dashboard_update': {'frequency': 'hourly'}
            },
            'monitoring': {
                'input_directories': ['input/', 'snapshots/'],
                'file_patterns': ['*.json', '*.csv', '*.html'],
                'auto_process': True,
                'batch_delay': 300  # 5 minutes
            },
            'notifications': {
                'discord_webhook': None,
                'email': {
                    'enabled': False,
                    'smtp_server': None,
                    'recipients': []
                }
            },
            'dashboard': {
                'google_sheets': {
                    'enabled': False,
                    'spreadsheet_id': None,
                    'credentials_path': None
                },
                'local_html': {
                    'enabled': True,
                    'output_path': 'output/dashboard.html'
                }
            },
            'pipeline': {
                'sites': [],
                'default_flags': ['--schema-matrix', '--emit-status', '--emit-drift-dashboard'],
                'timeout': 3600,  # 1 hour
                'retry_count': 2
            }
        }

    def save_config(self) -> None:
        """Save current configuration to file."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False)
            logger.info(f"Configuration saved to {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to save config: {e}")

    async def start_scheduler(self) -> None:
        """Start the scheduling system"""
        logger.info("Starting scheduler...")

        schedules_config = self.config['schedules']

        # Schedule scraping
        scraping_schedule = schedules_config['scraping']
        if scraping_schedule['frequency'] == 'daily':
            schedule.every().day.at(scraping_schedule['time']).do(
                self._run_scheduled_task, 'scraping'
            )

        # Schedule validation
        validation_schedule = schedules_config['validation']
        if validation_schedule['frequency'] == 'daily':
            schedule.every().day.at(validation_schedule['time']).do(
                self._run_scheduled_task, 'validation'
            )

        # Schedule export
        export_schedule = schedules_config['export']
        if export_schedule['frequency'] == 'weekly':
            getattr(schedule.every(), export_schedule['day']).at(export_schedule['time']).do(
                self._run_scheduled_task, 'export'
            )

        # Schedule list discovery if available
        if self.list_discovery:
            discovery_schedule = schedules_config.get('list_discovery', {})
            if discovery_schedule.get('enabled', True):
                frequency = discovery_schedule.get('frequency', 'hourly')

                if frequency == 'hourly':
                    schedule.every().hour.do(self._run_scheduled_task, 'list_discovery')
                elif frequency == 'daily':
                    time_str = discovery_schedule.get('time', '09:00')
                    schedule.every().day.at(time_str).do(self._run_scheduled_task, 'list_discovery')

                logger.info(f"List Discovery scheduled to run {frequency}")

        self.is_running = True

        # Main scheduler loop
        while self.is_running:
            schedule.run_pending()
            await asyncio.sleep(60)  # Check every minute

    def start_input_monitoring(self) -> None:
        """Start monitoring input directories"""
        logger.info("Starting input directory monitoring...")

        input_dirs = self.config['monitoring']['input_directories']

        if not self.observer:
            self.observer = Observer()

        for input_dir in input_dirs:
            dir_path = PROJECT_ROOT / input_dir
            if dir_path.exists():
                self.observer.schedule(self.input_monitor, str(dir_path), recursive=True)
                logger.info(f"Monitoring directory: {dir_path}")
            else:
                logger.warning(f"Input directory does not exist: {dir_path}")

        self.observer.start()
        self.is_running = True

        try:
            while self.is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop_monitoring()

    def stop_monitoring(self) -> None:
        """Stop input directory monitoring"""
        logger.info("Stopping input directory monitoring...")
        self.is_running = False
        if self.observer:
            self.observer.stop()
            self.observer.join()

    def process_input_file(self, file_path: Path) -> None:
        """Process a single input file"""
        logger.info(f"Processing input file: {file_path}")

        try:
            # Determine file type and processing strategy
            if file_path.suffix == '.json':
                self._process_json_input(file_path)
            elif file_path.suffix == '.csv':
                self._process_csv_input(file_path)
            elif file_path.suffix == '.html':
                self._process_html_input(file_path)
            else:
                logger.warning(f"Unknown file type: {file_path}")

        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            self.notifier.send_error_notification(
                f"Failed to process input file: {file_path}",
                str(e)
            )

    def _process_json_input(self, file_path: Path) -> None:
        """Process JSON input files"""
        with open(file_path, 'r') as f:
            data = json.load(f)

        # Check if it's a site list or data file
        if 'sites' in data:
            # Site list - trigger pipeline for each site
            for site in data['sites']:
                self.run_pipeline_for_site(site)
        else:
            # Data file - move to appropriate location and process
            logger.info(f"Processing data file: {file_path}")

    def _process_csv_input(self, file_path: Path) -> None:
        """Process CSV input files"""
        import pandas as pd  # type: ignore

        try:
            df = pd.read_csv(file_path)
            logger.info(f"Loaded CSV with {len(df)} rows: {file_path}")

            # If CSV contains site URLs, trigger processing
            if 'url' in df.columns or 'site' in df.columns:
                site_column = 'url' if 'url' in df.columns else 'site'
                for site in df[site_column].unique():
                    if pd.notna(site):
                        self.run_pipeline_for_site(str(site))

        except Exception as e:
            logger.error(f"Error processing CSV {file_path}: {e}")

    def _process_html_input(self, file_path: Path) -> None:
        """Process HTML input files (snapshots)"""
        # Move to snapshots directory if not already there
        if 'snapshots' not in str(file_path):
            snapshot_path = PROJECT_ROOT / 'snapshots' / file_path.name
            file_path.rename(snapshot_path)
            logger.info(f"Moved snapshot to: {snapshot_path}")

    def run_pipeline_for_site(self, site: str) -> None:
        """Run the full pipeline for a specific site"""
        logger.info(f"Running pipeline for site: {site}")

        try:
            success = self.pipeline.execute_pipeline(site)

            if success:
                self.notifier.send_success_notification(
                    f"Pipeline completed successfully for {site}"
                )
                self.dashboard.update_site_status(site, 'success')
            else:
                self.notifier.send_error_notification(
                    f"Pipeline failed for {site}",
                    "Check logs for details"
                )
                self.dashboard.update_site_status(site, 'failed')

        except Exception as e:
            logger.error(f"Pipeline execution failed for {site}: {e}")
            self.notifier.send_error_notification(
                f"Pipeline execution failed for {site}",
                str(e)
            )

    def _run_scheduled_task(self, task_type: str) -> None:
        """Run a scheduled task"""
        logger.info(f"Running scheduled task: {task_type}")

        try:
            if task_type == 'scraping':
                self._run_scraping_task()
            elif task_type == 'validation':
                self._run_validation_task()
            elif task_type == 'export':
                self._run_export_task()
            elif task_type == 'dashboard_update':
                self._run_dashboard_update()
            elif task_type == 'list_discovery' and self.list_discovery:
                self._run_list_discovery_task()

        except Exception as e:
            logger.error(f"Scheduled task {task_type} failed: {e}")
            self.notifier.send_error_notification(
                f"Scheduled task failed: {task_type}",
                str(e)
            )

    def _run_scraping_task(self) -> None:
        """Run scraping for all configured sites"""
        sites = self.config['pipeline']['sites']

        for site in sites:
            try:
                self.run_pipeline_for_site(site)
            except Exception as e:
                logger.error(f"Scraping failed for {site}: {e}")

    def _run_validation_task(self) -> None:
        """Run validation checks"""
        try:
            # Run module health check
            result = subprocess.run([
                sys.executable, '-m', 'universal_recon.utils.module_health_checker'
            ], capture_output=True, text=True, timeout=300)

            if result.returncode == 0:
                logger.info("Validation checks passed")
            else:
                logger.warning(f"Validation issues detected: {result.stderr}")

        except Exception as e:
            logger.error(f"Validation task failed: {e}")

    def _run_export_task(self) -> None:
        """Run export tasks"""
        try:
            # Export CSV summaries
            result = subprocess.run([
                sys.executable, '-m', 'universal_recon.analytics.export_csv_summary'
            ], capture_output=True, text=True, timeout=300)

            if result.returncode == 0:
                logger.info("Export task completed successfully")
            else:
                logger.error(f"Export task failed: {result.stderr}")

        except Exception as e:
            logger.error(f"Export task failed: {e}")

    def _run_dashboard_update(self) -> None:
        """Update the status dashboard"""
        try:
            self.dashboard.generate_dashboard()
            logger.info("Dashboard updated successfully")
        except Exception as e:
            logger.error(f"Dashboard update failed: {e}")

    def _run_list_discovery_task(self) -> None:
        """Run the list discovery process"""
        logger.info("Running list discovery task")

        try:
            if self.list_discovery:
                # Run single check for new files
                import asyncio
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)

                downloaded_files = loop.run_until_complete(
                    self.list_discovery.run_single_check()
                )

                if downloaded_files:
                    logger.info(f"List Discovery: Downloaded {len(downloaded_files)} new files")
                    # Process the downloaded files through the pipeline
                    for file_path in downloaded_files:
                        self.process_input_file(file_path)
                else:
                    logger.info("List Discovery: No new files found")
            else:
                logger.warning("List Discovery Agent not available")
        except Exception as e:
            logger.error(f"List discovery task failed: {e}")
            self.notifier.send_error_notification(
                "List discovery task failed",
                str(e)
            )

    def show_status(self) -> None:
        """Show current status and statistics"""
        print("\n" + "="*60)
        print("UNIVERSAL RUNNER STATUS")
        print("="*60)

        # Show scheduler status
        print(f"Scheduler running: {self.is_running}")
        print(f"Monitoring active: {self.observer and self.observer.is_alive() if self.observer else False}")

        # Show configuration
        print("\nConfiguration:")
        print(f"  Input directories: {', '.join(self.config['monitoring']['input_directories'])}")
        print(f"  File patterns: {', '.join(self.config['monitoring']['file_patterns'])}")

        # Show recent activity
        log_file = PROJECT_ROOT / 'logs' / 'automation' / 'universal_runner.log'
        if log_file.exists():
            with open(log_file, 'r') as f:
                lines = f.readlines()
                recent_lines = lines[-10:] if len(lines) >= 10 else lines
                print(f"\nRecent activity (last {len(recent_lines)} entries):")
                for line in recent_lines:
                    print(f"  {line.strip()}")

        print("\n" + "="*60)
        print("\n" + "="*60)
        print("UNIVERSAL RUNNER STATUS")

async def main() -> None:
    """Main entry point for Universal Project Runner."""
    parser = argparse.ArgumentParser(description="Universal Project Runner - Phase 3 Automation")
    parser.add_argument('--mode', choices=['schedule', 'watch', 'pipeline', 'status'], required=True,
                       help='Operation mode')
    parser.add_argument('--site', help='Site to process (for pipeline mode)')
    parser.add_argument('--input-dir', help='Input directory to monitor (for watch mode)')
    parser.add_argument('--frequency', choices=['daily', 'weekly', 'hourly'],
                       help='Schedule frequency (for schedule mode)')
    parser.add_argument('--dashboard', action='store_true', help='Generate dashboard (for status mode)')
    parser.add_argument('--config', help='Configuration file path')

    args = parser.parse_args()

    runner = UniversalRunner()

    try:
        if args.mode == 'schedule':
            logger.info("Starting scheduler mode...")
            await runner.start_scheduler()

        elif args.mode == 'watch':
            logger.info("Starting input monitoring mode...")
            if args.input_dir:
                # Override default input directories
                runner.config['monitoring']['input_directories'] = [args.input_dir]
            runner.start_input_monitoring()

        elif args.mode == 'pipeline':
            if not args.site:
                logger.error("Site argument required for pipeline mode")
                sys.exit(1)

            logger.info(f"Running pipeline for site: {args.site}")
            runner.run_pipeline_for_site(args.site)

        elif args.mode == 'status':
            if args.dashboard:
                runner.dashboard.generate_dashboard()
                logger.info("Dashboard generated")
            runner.show_status()

        elif args.mode == 'monitor':
            if args.input_dir:
                # Override default input directories
                runner.config['monitoring']['input_directories'] = [args.input_dir]
            runner.start_input_monitoring()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        runner.stop_monitoring()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
