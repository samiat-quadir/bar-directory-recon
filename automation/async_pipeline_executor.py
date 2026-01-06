#!/usr/bin/env python3
"""
Async Pipeline Executor
=======================

Provides asynchronous execution of site pipelines with concurrent processing.
This executor significantly improves performance over synchronous execution
by processing multiple sites concurrently using asyncio.

Features:
    - Concurrent site processing with configurable concurrency limit
    - Automatic retry with exponential backoff
    - Real-time progress reporting
    - Graceful error handling and logging
"""

import asyncio
import logging
import time
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class AsyncPipelineExecutor:
    """
    Async version of PipelineExecutor with concurrent execution.

    Provides significant performance improvements for multi-site processing
    through asyncio-based concurrent execution.

    Attributes:
        config: Configuration dictionary containing execution parameters
        timeout: Maximum time in seconds for each site processing
        max_concurrent: Maximum number of sites to process concurrently
        retry_count: Number of retry attempts for failed sites
    """

    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize the AsyncPipelineExecutor.

        Args:
            config: Configuration dictionary with keys:
                - timeout: Max execution time per site (default: 3600)
                - max_concurrent_sites: Concurrent execution limit (default: 5)
                - retry_count: Retry attempts for failures (default: 3)
                - demo_mode: Whether to run in demo mode (default: False)
        """
        self.config = config
        self.timeout = config.get("timeout", 3600)
        self.max_concurrent = config.get("max_concurrent_sites", 5)
        self.retry_count = config.get("retry_count", 3)
        self.project_root = Path(__file__).parent.parent

        # Create semaphore for concurrency control
        self.semaphore: Optional[asyncio.Semaphore] = None

        # Demo mode for testing
        self.demo_mode = config.get("demo_mode", False)

        logger.info(
            f"AsyncPipelineExecutor initialized with {self.max_concurrent} concurrent slots"
        )

    def _get_semaphore(self) -> asyncio.Semaphore:
        """Get or create the semaphore (must be created within async context)."""
        if self.semaphore is None:
            self.semaphore = asyncio.Semaphore(self.max_concurrent)
        return self.semaphore

    async def run_all_async(self, sites: List[str]) -> Dict[str, bool]:
        """
        Run pipeline for all sites asynchronously with asyncio.gather.

        Args:
            sites: List of site URLs to process

        Returns:
            Dict mapping site names to success status (True/False)
        """
        logger.info(f"Starting async execution for {len(sites)} sites")
        start_time = time.time()

        # Create async tasks for all sites
        tasks = [self._execute_site_with_semaphore(site) for site in sites]

        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        site_results: Dict[str, bool] = {}
        for site, result in zip(sites, results):
            if isinstance(result, Exception):
                logger.error(f"Site {site} failed with exception: {result}")
                site_results[site] = False
            else:
                site_results[site] = bool(result)

        execution_time = time.time() - start_time
        success_count = sum(1 for success in site_results.values() if success)

        logger.info(f"Async execution completed in {execution_time:.2f}s")
        logger.info(
            f"Success rate: {success_count}/{len(sites)} "
            f"({success_count/len(sites)*100:.1f}%)"
        )

        return site_results

    async def _execute_site_with_semaphore(self, site: str) -> bool:
        """
        Execute pipeline for a site with concurrency control.

        Args:
            site: Site URL to process

        Returns:
            True if successful, False otherwise
        """
        semaphore = self._get_semaphore()
        async with semaphore:
            return await self._execute_pipeline_async(site)

    async def _execute_pipeline_async(self, site: str) -> bool:
        """
        Execute pipeline for a specific site asynchronously.

        Implements retry logic with exponential backoff.

        Args:
            site: Site URL to process

        Returns:
            True if successful, False otherwise
        """
        for attempt in range(self.retry_count):
            try:
                logger.info(f"Executing pipeline for {site} (attempt {attempt + 1})")

                if self.demo_mode:
                    # Simulate processing time
                    processing_time = 2 + (attempt * 0.5)
                    await asyncio.sleep(processing_time)

                    # Simulate success/failure (90% success rate)
                    import random

                    success = random.random() > 0.1

                    if success:
                        logger.info(f"Site {site} completed successfully (simulated)")
                        return True
                    else:
                        logger.warning(
                            f"Site {site} attempt {attempt + 1} failed (simulated)"
                        )
                else:
                    # Real pipeline execution
                    loop = asyncio.get_event_loop()
                    result = await loop.run_in_executor(
                        None,  # Use default executor
                        self._run_pipeline_subprocess,
                        site,
                    )

                    if result:
                        logger.info(f"Site {site} completed successfully")
                        return True
                    else:
                        logger.warning(f"Site {site} attempt {attempt + 1} failed")

            except Exception as e:
                logger.error(f"Site {site} attempt {attempt + 1} error: {e}")

            # Exponential backoff between retries
            if attempt < self.retry_count - 1:
                delay = 2**attempt
                await asyncio.sleep(delay)

        logger.error(f"Site {site} failed after {self.retry_count} attempts")
        return False

    def _run_pipeline_subprocess(self, site: str) -> bool:
        """
        Run the actual subprocess (blocking operation).

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

    async def run_with_progress(self, sites: List[str]) -> Dict[str, bool]:
        """
        Run pipeline with real-time progress reporting.

        Args:
            sites: List of site URLs to process

        Returns:
            Dict mapping site names to success status
        """
        completed: Dict[str, bool] = {}
        pending_tasks = {
            asyncio.create_task(
                self._execute_site_with_semaphore(site), name=site
            ): site
            for site in sites
        }

        logger.info(f"Starting processing of {len(sites)} sites with progress...")

        while pending_tasks:
            done, pending = await asyncio.wait(
                pending_tasks, return_when=asyncio.FIRST_COMPLETED
            )

            for task in done:
                site = pending_tasks.pop(task)
                try:
                    result = await task
                    completed[site] = result
                    status = "SUCCESS" if result else "FAILED"
                    logger.info(
                        f"Progress: {len(completed)}/{len(sites)} - {site}: {status}"
                    )
                except Exception as e:
                    logger.error(f"Site {site} failed: {e}")
                    completed[site] = False

            pending_tasks = {
                task: site for task, site in pending_tasks.items() if task in pending
            }

        return completed
