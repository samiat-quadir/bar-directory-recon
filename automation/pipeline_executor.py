#!/usr/bin/env python3
"""
Pipeline Executor
=================

Synchronous pipeline executor for site processing.
Provides a fallback when async execution is not desired.
"""

import logging
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class PipelineExecutor:
    """
    Synchronous pipeline executor for site processing.

    Processes sites sequentially, suitable for single-site operations
    or when async execution is not available/desired.
    """

    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize the PipelineExecutor.

        Args:
            config: Configuration dictionary with execution parameters
        """
        self.config = config
        self.timeout = config.get("timeout", 3600)
        self.retry_count = config.get("retry_count", 3)
        self.project_root = Path(__file__).parent.parent

        logger.info("PipelineExecutor initialized")

    def run_all(self, sites: List[str]) -> Dict[str, bool]:
        """
        Run pipeline for all sites sequentially.

        Args:
            sites: List of site URLs to process

        Returns:
            Dict mapping site names to success status
        """
        logger.info(f"Starting sequential execution for {len(sites)} sites")
        start_time = time.time()

        results: Dict[str, bool] = {}
        for site in sites:
            results[site] = self._execute_pipeline(site)

        execution_time = time.time() - start_time
        success_count = sum(1 for success in results.values() if success)

        logger.info(f"Sequential execution completed in {execution_time:.2f}s")
        logger.info(
            f"Success rate: {success_count}/{len(sites)} "
            f"({success_count/len(sites)*100:.1f}%)"
        )

        return results

    def _execute_pipeline(self, site: str) -> bool:
        """
        Execute pipeline for a specific site.

        Args:
            site: Site URL to process

        Returns:
            True if successful, False otherwise
        """
        for attempt in range(self.retry_count):
            try:
                logger.info(f"Executing pipeline for {site} (attempt {attempt + 1})")

                result = self._run_pipeline_subprocess(site)

                if result:
                    logger.info(f"Site {site} completed successfully")
                    return True
                else:
                    logger.warning(f"Site {site} attempt {attempt + 1} failed")

            except Exception as e:
                logger.error(f"Site {site} attempt {attempt + 1} error: {e}")

            # Delay between retries
            if attempt < self.retry_count - 1:
                delay = 2**attempt
                time.sleep(delay)

        logger.error(f"Site {site} failed after {self.retry_count} attempts")
        return False

    def _run_pipeline_subprocess(self, site: str) -> bool:
        """
        Run the actual subprocess.

        Args:
            site: Site URL to process

        Returns:
            True if subprocess completed successfully, False otherwise
        """
        cmd = [
            sys.executable,
            "-m",
            "universal_recon.main",
            "--site",
            site,
            "--schema-matrix",
            "--emit-status",
        ]

        try:
            result = subprocess.run(
                cmd,
                timeout=self.timeout,
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            logger.error(f"Site {site} timed out after {self.timeout}s")
            return False
        except Exception as e:
            logger.error(f"Site {site} subprocess error: {e}")
            return False
