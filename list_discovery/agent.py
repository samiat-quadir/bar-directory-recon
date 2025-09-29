"""
List Discovery Agent - Phase 4
=============================

Monitors city/county web pages for new file uploads (PDF, CSV, XLS) and automatically
downloads them to the input/ directory for processing. Integrates with the Universal
Project Runner for seamless automation.

Features:
- Web page monitoring with change detection
- File download automation
- Discord/Email notifications
- CLI interface for manual and scheduled runs
- Integration with existing pipeline automation
"""

import argparse
import asyncio
import hashlib
import json
import logging
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse

# Optional imports with fallbacks
try:
    import aiohttp

    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False

try:
    import aiofiles

    AIOFILES_AVAILABLE = True
except ImportError:
    AIOFILES_AVAILABLE = False

try:
    from bs4 import BeautifulSoup

    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(
            PROJECT_ROOT / "logs" / "automation" / "list_discovery.log"
        ),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)

# Import automation modules
try:
    from automation.notifier import NotificationManager
except ImportError:
    logger.warning("NotificationManager not available - notifications will be disabled")
    NotificationManager = None


class WebPageMonitor:
    """Monitors web pages for changes and new file uploads"""

    config: Dict[str, Any]
    monitored_urls: List[Dict[str, Any]]
    download_dir: Path
    state_file: Path
    file_extensions: List[str]
    check_interval: int
    notifier: Optional[Any]
    state: Dict[str, Any]

    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config
        self.monitored_urls = config.get("monitored_urls", [])
        self.download_dir = Path(config.get("download_dir", "input/discovered_lists"))
        self.state_file = Path(config.get("state_file", "list_discovery/state.json"))
        self.file_extensions = config.get(
            "file_extensions", [".pdf", ".csv", ".xls", ".xlsx"]
        )
        self.check_interval = config.get("check_interval", 3600)  # 1 hour default

        # Ensure directories exist
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

        # Initialize notification manager
        self.notifier = None
        if NotificationManager:
            notifications_config = config.get("notifications", {})
            self.notifier = NotificationManager(notifications_config)

        # Load previous state
        self.state = self._load_state()

    def _load_state(self) -> Dict[str, Any]:
        """Load previous monitoring state"""
        try:
            if self.state_file.exists():
                with open(self.state_file, "r") as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load state: {e}")

        return {
            "last_check": None,
            "discovered_files": {},
            "page_hashes": {},
            "download_history": [],
        }

    def _save_state(self) -> None:
        """Save current monitoring state"""
        try:
            self.state["last_check"] = datetime.now().isoformat()
            with open(self.state_file, "w") as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save state: {e}")

    def _get_page_hash(self, content: str) -> str:
        """Generate hash of page content for change detection"""
        return hashlib.md5(content.encode("utf-8")).hexdigest()

    def _extract_file_links(self, url: str, html_content: str) -> List[Tuple[str, str]]:
        """Extract file download links from HTML content"""
        soup = BeautifulSoup(html_content, "html.parser")
        file_links = []

        # Find all links
        for link in soup.find_all("a", href=True):
            href = link["href"]

            # Convert relative URLs to absolute
            full_url = urljoin(url, href)

            # Check if link points to a file we're interested in
            parsed_url = urlparse(full_url)
            path = parsed_url.path.lower()

            for ext in self.file_extensions:
                if path.endswith(ext):
                    # Extract filename from URL or link text
                    filename = os.path.basename(parsed_url.path)
                    if not filename:
                        filename = link.get_text(strip=True)[
                            :50
                        ]  # Fallback to link text

                    file_links.append((full_url, filename))
                    break

        return file_links

    async def _download_file(
        self, session: Any, url: str, filename: str
    ) -> Optional[Path]:
        """Download a file to the download directory"""
        try:
            # Sanitize filename
            safe_filename = re.sub(r"[^\w\s.-]", "_", filename)
            if not any(
                safe_filename.lower().endswith(ext) for ext in self.file_extensions
            ):
                # Add extension if missing
                parsed_url = urlparse(url)
                path_ext = os.path.splitext(parsed_url.path)[1]
                if path_ext:
                    safe_filename += path_ext

            # Add timestamp to avoid conflicts
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            name, ext = os.path.splitext(safe_filename)
            final_filename = f"{name}_{timestamp}{ext}"

            file_path = self.download_dir / final_filename

            logger.info(f"Downloading {url} to {file_path}")

            async with session.get(url) as response:
                if response.status == 200:
                    async with aiofiles.open(file_path, "wb") as f:
                        async for chunk in response.content.iter_chunked(8192):
                            await f.write(chunk)

                    logger.info(f"Successfully downloaded: {file_path}")
                    return file_path
                else:
                    logger.error(f"Failed to download {url}: HTTP {response.status}")
                    return None

        except Exception as e:
            logger.error(f"Error downloading {url}: {e}")
            return None

    async def _check_url(self, session: Any, url_config: Dict[str, Any]) -> List[Path]:
        """Check a single URL for new files"""
        url = url_config["url"]
        name = url_config.get("name", url)

        try:
            logger.info(f"Checking {name}: {url}")

            async with session.get(url) as response:
                if response.status != 200:
                    logger.error(f"Failed to fetch {url}: HTTP {response.status}")
                    return []

                html_content = await response.text()

            # Check if page has changed
            current_hash = self._get_page_hash(html_content)
            previous_hash = self.state["page_hashes"].get(url)

            if previous_hash and current_hash == previous_hash:
                logger.debug(f"No changes detected for {name}")
                return []

            # Update hash
            self.state["page_hashes"][url] = current_hash

            # Extract file links
            file_links = self._extract_file_links(url, html_content)

            if not file_links:
                logger.info(f"No file links found on {name}")
                return []

            # Check for new files
            discovered_files = self.state["discovered_files"].get(url, set())
            if isinstance(discovered_files, list):
                discovered_files = set(discovered_files)

            new_files = []
            downloaded_files = []

            for file_url, filename in file_links:
                if file_url not in discovered_files:
                    logger.info(f"New file discovered: {filename} from {name}")
                    new_files.append((file_url, filename))
                    discovered_files.add(file_url)

                    # Download the file
                    downloaded_path = await self._download_file(
                        session, file_url, filename
                    )
                    if downloaded_path:
                        downloaded_files.append(downloaded_path)

                        # Record download in history
                        self.state["download_history"].append(
                            {
                                "url": file_url,
                                "filename": filename,
                                "source_page": url,
                                "source_name": name,
                                "downloaded_path": str(downloaded_path),
                                "timestamp": datetime.now().isoformat(),
                            }
                        )

            # Update discovered files
            self.state["discovered_files"][url] = list(discovered_files)

            # Send notifications for new files
            if new_files and self.notifier:
                self._send_discovery_notification(name, new_files, downloaded_files)

            return downloaded_files

        except Exception as e:
            logger.error(f"Error checking {url}: {e}")
            return []

    def _send_discovery_notification(
        self,
        source_name: str,
        new_files: List[Tuple[str, str]],
        downloaded_files: List[Path],
    ) -> None:
        """Send notification about newly discovered files"""
        if not self.notifier:
            return

        title = f"New Lists Discovered: {source_name}"

        file_list = "\n".join([f"• {filename}" for _, filename in new_files])
        download_list = "\n".join([f"• {path.name}" for path in downloaded_files])

        message = f"""
New files discovered from {source_name}:

Files Found:
{file_list}

Downloaded Files:
{download_list}

Files are ready for processing in the input directory.
        """

        self.notifier.send_success_notification(title, message.strip())

    async def check_all_urls(self) -> List[Path]:
        """Check all monitored URLs for new files"""
        if not self.monitored_urls:
            logger.warning("No URLs configured for monitoring")
            return []

        all_downloaded_files = []

        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=60),
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            },
        ) as session:
            for url_config in self.monitored_urls:
                try:
                    downloaded_files = await self._check_url(session, url_config)
                    all_downloaded_files.extend(downloaded_files)

                    # Brief pause between requests to be respectful
                    await asyncio.sleep(2)

                except Exception as e:
                    logger.error(
                        f"Error processing URL {url_config.get('url', 'unknown')}: {e}"
                    )

        # Save state after checking all URLs
        self._save_state()

        return all_downloaded_files

    async def monitor_continuously(self) -> None:
        """Continuously monitor URLs at specified intervals"""
        logger.info(
            f"Starting continuous monitoring (check interval: {self.check_interval}s)"
        )

        while True:
            try:
                logger.info("Starting scheduled check for new files...")
                downloaded_files = await self.check_all_urls()

                if downloaded_files:
                    logger.info(f"Downloaded {len(downloaded_files)} new files")
                else:
                    logger.info("No new files discovered")

                # Wait for next check
                logger.info(f"Waiting {self.check_interval}s until next check...")
                await asyncio.sleep(self.check_interval)

            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                # Wait before retrying
                await asyncio.sleep(60)

    def get_statistics(self) -> Dict[str, Any]:
        """Get monitoring statistics"""
        total_discovered = sum(
            len(files) if isinstance(files, list) else len(files)
            for files in self.state["discovered_files"].values()
        )

        recent_downloads = [
            item
            for item in self.state["download_history"]
            if datetime.fromisoformat(item["timestamp"])
            > datetime.now() - timedelta(days=7)
        ]

        return {
            "monitored_urls": len(self.monitored_urls),
            "total_files_discovered": total_discovered,
            "total_downloads": len(self.state["download_history"]),
            "recent_downloads_7days": len(recent_downloads),
            "last_check": self.state.get("last_check"),
            "download_directory": str(self.download_dir),
        }


class ListDiscoveryAgent:
    """Main List Discovery Agent class"""

    config_path: Path
    config: Dict[str, Any]
    monitor: WebPageMonitor

    def __init__(self, config_path: str = "list_discovery/config.yaml") -> None:
        self.config_path = PROJECT_ROOT / config_path
        self.config = self._load_config()
        self.monitor = WebPageMonitor(self.config)

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            if self.config_path.exists():
                with open(self.config_path, "r") as f:
                    return yaml.safe_load(f)
        except Exception as e:
            logger.warning(f"Failed to load config: {e}")

        # Return default configuration
        return {
            "monitored_urls": [],
            "download_dir": "input/discovered_lists",
            "file_extensions": [".pdf", ".csv", ".xls", ".xlsx"],
            "check_interval": 3600,  # 1 hour
            "notifications": {"discord_webhook": None, "email": {"enabled": False}},
        }

    def save_config(self) -> None:
        """Save current configuration to file"""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, "w") as f:
                yaml.dump(self.config, f, default_flow_style=False)
            logger.info(f"Configuration saved to {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to save config: {e}")

    async def run_single_check(self) -> List[Path]:
        """Run a single check of all monitored URLs"""
        logger.info("Running single check for new files...")
        downloaded_files = await self.monitor.check_all_urls()

        if downloaded_files:
            logger.info(f"✅ Downloaded {len(downloaded_files)} new files:")
            for file_path in downloaded_files:
                logger.info(f"  📄 {file_path}")
        else:
            logger.info("ℹ️ No new files discovered")

        return downloaded_files

    async def start_monitoring(self) -> None:
        """Start continuous monitoring"""
        await self.monitor.monitor_continuously()

    def show_status(self) -> None:
        """Show current status and statistics"""
        stats = self.monitor.get_statistics()

        print("\n" + "=" * 60)
        print("📋 LIST DISCOVERY AGENT STATUS")
        print("=" * 60)

        print(f"Monitored URLs: {stats['monitored_urls']}")
        print(f"Total files discovered: {stats['total_files_discovered']}")
        print(f"Total downloads: {stats['total_downloads']}")
        print(f"Recent downloads (7 days): {stats['recent_downloads_7days']}")
        print(f"Download directory: {stats['download_directory']}")

        if stats["last_check"]:
            last_check = datetime.fromisoformat(stats["last_check"])
            print(f"Last check: {last_check.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print("Last check: Never")

        # Show configured URLs
        if self.config["monitored_urls"]:
            print(f"\n📍 Configured URLs ({len(self.config['monitored_urls'])}):")
            for i, url_config in enumerate(self.config["monitored_urls"], 1):
                name = url_config.get("name", "Unnamed")
                url = url_config["url"]
                print(f"  {i}. {name}: {url}")
        else:
            print("\n⚠️ No URLs configured for monitoring")

        print("\n" + "=" * 60)

    def add_url(self, url: str, name: Optional[str] = None) -> bool:
        """Add a URL to monitor"""
        if not name:
            name = urlparse(url).netloc

        url_config = {"url": url, "name": name}

        # Check if URL already exists
        for existing in self.config["monitored_urls"]:
            if existing["url"] == url:
                logger.warning(f"URL already exists: {url}")
                return False

        self.config["monitored_urls"].append(url_config)
        self.save_config()

        logger.info(f"Added URL: {name} ({url})")
        return True

    def remove_url(self, url_or_index: Any) -> bool:
        """Remove a URL from monitoring"""
        try:
            # Try to parse as index
            if isinstance(url_or_index, str) and url_or_index.isdigit():
                index = int(url_or_index) - 1
                if 0 <= index < len(self.config["monitored_urls"]):
                    removed = self.config["monitored_urls"].pop(index)
                    self.save_config()
                    logger.info(f"Removed URL: {removed['name']} ({removed['url']})")
                    return True
                else:
                    logger.error(f"Invalid index: {url_or_index}")
                    return False

            # Try to match by URL
            for i, url_config in enumerate(self.config["monitored_urls"]):
                if url_config["url"] == url_or_index:
                    removed = self.config["monitored_urls"].pop(i)
                    self.save_config()
                    logger.info(f"Removed URL: {removed['name']} ({removed['url']})")
                    return True

            logger.error(f"URL not found: {url_or_index}")
            return False

        except Exception as e:
            logger.error(f"Error removing URL: {e}")
            return False


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="List Discovery Agent - Phase 4")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Check command
    subparsers.add_parser("check", help="Run single check for new files")

    # Monitor command
    monitor_parser = subparsers.add_parser(
        "monitor", help="Start continuous monitoring"
    )
    monitor_parser.add_argument(
        "--interval", type=int, help="Check interval in seconds"
    )

    # Status command
    subparsers.add_parser("status", help="Show current status and statistics")

    # Add URL command
    add_parser = subparsers.add_parser("add", help="Add URL to monitor")
    add_parser.add_argument("url", help="URL to monitor")
    add_parser.add_argument("--name", help="Display name for the URL")

    # Remove URL command
    remove_parser = subparsers.add_parser("remove", help="Remove URL from monitoring")
    remove_parser.add_argument("url_or_index", help="URL or index number to remove")

    # List URLs command
    subparsers.add_parser("list", help="List all configured URLs")

    # Setup command
    subparsers.add_parser("setup", help="Setup initial configuration")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Initialize agent
    agent = ListDiscoveryAgent()

    try:
        if args.command == "check":
            downloaded_files = await agent.run_single_check()
            print(f"\n✅ Check complete. Downloaded {len(downloaded_files)} files.")

        elif args.command == "monitor":
            if args.interval:
                agent.config["check_interval"] = args.interval
            await agent.start_monitoring()

        elif args.command == "status":
            agent.show_status()

        elif args.command == "add":
            if agent.add_url(args.url, args.name):
                print(f"✅ Added URL: {args.url}")
            else:
                print(f"❌ Failed to add URL: {args.url}")

        elif args.command == "remove":
            if agent.remove_url(args.url_or_index):
                print("✅ Removed URL")
            else:
                print("❌ Failed to remove URL")

        elif args.command == "list":
            agent.show_status()

        elif args.command == "setup":
            print("🛠️ Setting up List Discovery Agent...")

            # Create default config with examples
            default_config = {
                "monitored_urls": [
                    {
                        "url": "https://example-county.gov/licenses",
                        "name": "Example County Liquor Licenses",
                    }
                ],
                "download_dir": "input/discovered_lists",
                "file_extensions": [".pdf", ".csv", ".xls", ".xlsx"],
                "check_interval": 3600,
                "notifications": {
                    "discord_webhook": None,
                    "email": {
                        "enabled": False,
                        "smtp_server": "smtp.gmail.com",
                        "username": "",
                        "recipients": [],
                    },
                },
            }

            agent.config = default_config
            agent.save_config()

            print(f"✅ Configuration created: {agent.config_path}")
            print("📝 Edit the configuration file to add your target URLs")
            print("🚀 Run 'python list_discovery/agent.py status' to see current setup")

    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
