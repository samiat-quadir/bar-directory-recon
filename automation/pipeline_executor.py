from typing import Any, Dict, List, Optional
"""
Pipeline Executor for Universal Project Runner
============================================

Executes the universal recon pipeline for sites with proper error handling,
logging, and timeout management.
"""


import logging
import subprocess
import sys
import time
from pathlib import Path

from datetime import datetime
try:
    from loguru import logger as loguru_logger
    LOGURU_AVAILABLE = True
except ImportError:
    LOGURU_AVAILABLE = False


def setup_logging(log_dir: Path, use_loguru: bool = False) -> None:
    log_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = log_dir / f'pipeline_run_{timestamp}.log'
    if use_loguru and LOGURU_AVAILABLE:
        loguru_logger.add(
            str(log_file),
            level="INFO",
            format=(
                "<green>{time}</green> <level>{level}</level> "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
                "<level>{message}</level>"
            )
        )
    else:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s %(levelname)s %(name)s: %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )

logger = loguru_logger if LOGURU_AVAILABLE else logging.getLogger(__name__)




class PipelineExecutor:
    """Executes recon pipeline for sites."""
    config: Dict[str, Any]
    timeout: int
    retry_count: int
    default_flags: List[str]
    project_root: Path


    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config
        self.timeout = config.get('timeout', 3600)  # 1 hour default
        self.retry_count = config.get('retry_count', 3)
        self.default_flags = config.get('default_flags', ['--schema-matrix', '--emit-status'])
        self.project_root = Path(__file__).parent.parent
        # Config toggle for demo/test vs. prod mode
        self.demo_mode = config.get('demo_mode', False)
        # Ensure required folders exist
        self.output_dir = self.project_root / 'output'
        self.input_dir = self.project_root / 'input'
        self.logs_dir = self.project_root / 'logs'
        for d in [self.output_dir, self.input_dir, self.logs_dir]:
            d.mkdir(parents=True, exist_ok=True)
        # Setup logging
        setup_logging(self.logs_dir, use_loguru=LOGURU_AVAILABLE)

    def execute_pipeline(self, site: str, flags: Optional[List[str]] = None) -> bool:
        """Execute pipeline for a specific site."""
        if flags is None:
            flags = self.default_flags.copy()
        # Ensure site flag is included
        if '--site' not in flags:
            flags.extend(['--site', site])
        attempt = 0
        while attempt < self.retry_count:
            try:
                logger.info(f"Executing pipeline for {site} (attempt {attempt + 1}/{self.retry_count})")
                # Build command
                cmd = [
                    sys.executable,
                    '-m', 'universal_recon.main'
                ] + flags
                # Log command being executed
                logger.debug(f"Executing command: {' '.join(cmd)}")
                # Execute with timeout
                result = subprocess.run(
                    cmd,
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout
                )
                # Log output
                if result.stdout:
                    logger.info(f"Pipeline output for {site}:\n{result.stdout}")
                if result.stderr:
                    logger.warning(f"Pipeline stderr for {site}:\n{result.stderr}")
                # Check result
                if result.returncode == 0:
                    logger.info(f"Pipeline completed successfully for {site}")
                    logger.info(f"--- Pipeline run summary for {site}: SUCCESS ---")
                    return True
                else:
                    logger.error(f"Pipeline failed for {site} with return code {result.returncode}")
            except subprocess.TimeoutExpired:
                logger.error(f"Pipeline timed out for {site} after {self.timeout} seconds")
            except Exception as e:
                logger.error(f"Pipeline execution failed for {site}: {e}")
            attempt += 1
            if attempt < self.retry_count:
                wait_time = 2 ** attempt  # Exponential backoff
                logger.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
        logger.error(f"Pipeline failed for {site} after {self.retry_count} attempts")
        logger.info(f"--- Pipeline run summary for {site}: FAILURE ---")
        return False

    def execute_batch(self, sites: List[str], flags: Optional[List[str]] = None) -> Dict[str, bool]:
        """Execute pipeline for multiple sites."""
        results: Dict[str, bool] = {}
        for site in sites:
            try:
                success = self.execute_pipeline(site, flags)
                results[site] = success
                # Brief pause between sites to avoid overwhelming system
                time.sleep(5)
            except Exception as e:
                logger.error(f"Failed to execute pipeline for {site}: {e}")
                results[site] = False
        logger.info("=== Batch pipeline run summary ===")
        for site, result in results.items():
            logger.info(f"  {site}: {'SUCCESS' if result else 'FAILURE'}")
        logger.info("=== End of batch summary ===")
        return results

    def validate_environment(self) -> bool:
        """Validate that the environment is ready for pipeline execution."""
        try:
            # Check if main module exists
            main_module = self.project_root / 'universal_recon' / 'main.py'
            if not main_module.exists():
                logger.error(f"Main module not found: {main_module}")
                return False
            # Check if Python can import the module
            result = subprocess.run([
                sys.executable, '-c', 'import universal_recon.main'
            ], capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                logger.error(f"Failed to import universal_recon.main: {result.stderr}")
                return False
            logger.info("Environment validation passed")
            return True
        except Exception as e:
            logger.error(f"Environment validation failed: {e}")
            return False

    def get_available_sites(self) -> List[str]:
        """Get list of available sites from configuration."""
        sites = self.config.get('sites', [])
        if isinstance(sites, list):
            return [str(site) for site in sites]
        return []

    def add_site(self, site: str) -> None:
        """Add a site to the configuration."""
        if 'sites' not in self.config:
            self.config['sites'] = []
        if site not in self.config['sites']:
            self.config['sites'].append(site)
            logger.info(f"Added site to configuration: {site}")

    def execute_validation_check(self) -> bool:
        """Execute validation checks on the system."""
        try:
            logger.info("Running system validation checks...")
            # Run module health checker
            result = subprocess.run([
                sys.executable, '-m', 'universal_recon.utils.module_health_checker'
            ], capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                logger.info("Module health check passed")
                return True
            else:
                logger.warning(f"Module health check issues: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Validation check failed: {e}")
            return False

    def execute_export_tasks(self) -> bool:
        """Execute export tasks."""
        try:
            logger.info("Running export tasks...")
            # Export CSV summaries
            result = subprocess.run([
                sys.executable, '-m', 'universal_recon.analytics.export_csv_summary'
            ], capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                logger.info("Export tasks completed successfully")
                return True
            else:
                logger.error(f"Export tasks failed: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Export tasks failed: {e}")
            return False

    def get_pipeline_status(self, site: str) -> Dict[str, Any]:
        """Get status information for a site."""
        try:
            # Check if output files exist for the site
            output_dir = self.project_root / 'output'
            status: Dict[str, Any] = {
                'site': site,
                'has_fieldmap': False,
                'has_report': False,
                'has_matrix': False,
                'last_run': None
            }
            # Check for fieldmap
            fieldmap_file = output_dir / 'fieldmap' / f'{site}_fieldmap.json'
            if fieldmap_file.exists():
                status['has_fieldmap'] = True
                status['last_run'] = fieldmap_file.stat().st_mtime
            # Check for report
            report_file = output_dir / 'reports' / f'{site}_full_report.json'
            if report_file.exists():
                status['has_report'] = True
                if not status['last_run'] or report_file.stat().st_mtime > status['last_run']:
                    status['last_run'] = report_file.stat().st_mtime
            # Check for schema matrix
            matrix_file = output_dir / 'schema_matrix.json'
            if matrix_file.exists():
                status['has_matrix'] = True
            return status
        except Exception as e:
            logger.error(f"Failed to get pipeline status for {site}: {e}")
            return {'site': site, 'error': str(e)}
