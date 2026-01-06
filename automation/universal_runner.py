#!/usr/bin/env python3
"""
Universal Runner
================

Unified interface for running pipelines with support for both
synchronous and asynchronous execution modes.
"""

import asyncio
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from .async_pipeline_executor import AsyncPipelineExecutor
from .pipeline_executor import PipelineExecutor

logger = logging.getLogger(__name__)


class UniversalRunner:
    """
    Universal runner that supports both sync and async pipeline execution.

    Provides a unified interface for running pipelines, automatically
    selecting the appropriate executor based on configuration.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize the UniversalRunner.

        Args:
            config: Configuration dictionary. If None, loads from config.yaml
        """
        if config is None:
            config = self._load_config()

        self.config = config
        self.use_async = config.get("pipeline", {}).get("use_async", True)

        # Initialize executors
        pipeline_config = config.get("pipeline", {})
        self.sync_executor = PipelineExecutor(pipeline_config)
        self.async_executor = AsyncPipelineExecutor(pipeline_config)

        logger.info(
            f"UniversalRunner initialized (async_mode: {self.use_async})"
        )

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from config.yaml."""
        config_path = Path(__file__).parent / "config.yaml"

        if config_path.exists():
            with open(config_path) as f:
                return yaml.safe_load(f) or {}
        else:
            logger.warning(f"Config file not found at {config_path}, using defaults")
            return self._default_config()

    def _default_config(self) -> Dict[str, Any]:
        """Return default configuration."""
        return {
            "pipeline": {
                "use_async": True,
                "max_concurrent_sites": 5,
                "timeout": 3600,
                "retry_count": 3,
            }
        }

    def run_pipeline(
        self, sites: List[str], use_async: Optional[bool] = None
    ) -> Dict[str, bool]:
        """
        Run the pipeline for the specified sites.

        Args:
            sites: List of site URLs to process
            use_async: Override async setting. If None, uses config setting.

        Returns:
            Dict mapping site names to success status
        """
        should_use_async = use_async if use_async is not None else self.use_async

        if should_use_async:
            try:
                return asyncio.run(self.run_pipeline_async(sites))
            except Exception as e:
                logger.warning(
                    f"Async execution failed ({e}), falling back to sync"
                )
                return self.sync_executor.run_all(sites)
        else:
            return self.sync_executor.run_all(sites)

    async def run_pipeline_async(self, sites: List[str]) -> Dict[str, bool]:
        """
        Run the pipeline asynchronously.

        Args:
            sites: List of site URLs to process

        Returns:
            Dict mapping site names to success status
        """
        return await self.async_executor.run_all_async(sites)

    async def run_pipeline_with_progress(self, sites: List[str]) -> Dict[str, bool]:
        """
        Run the pipeline with real-time progress reporting.

        Args:
            sites: List of site URLs to process

        Returns:
            Dict mapping site names to success status
        """
        return await self.async_executor.run_with_progress(sites)


def main() -> None:
    """CLI entry point for the universal runner."""
    import argparse

    parser = argparse.ArgumentParser(description="Universal Pipeline Runner")
    parser.add_argument("--sites", nargs="+", required=True, help="Sites to process")
    parser.add_argument("--sync", action="store_true", help="Force synchronous mode")
    parser.add_argument(
        "--async", action="store_true", dest="async_mode",
        help="Force asynchronous mode"
    )

    args = parser.parse_args()

    runner = UniversalRunner()

    use_async = None
    if args.sync:
        use_async = False
    elif args.async_mode:
        use_async = True

    results = runner.run_pipeline(args.sites, use_async=use_async)

    # Print summary
    success_count = sum(1 for s in results.values() if s)
    print(f"\nResults: {success_count}/{len(results)} sites succeeded")
    for site, success in results.items():
        status = "✅" if success else "❌"
        print(f"  {status} {site}")


if __name__ == "__main__":
    main()
