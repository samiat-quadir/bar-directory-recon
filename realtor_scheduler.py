"""
Realtor Directory Automation Scheduler
Weekly automated lead extraction script
"""

import os
import schedule
import time
import logging
from datetime import datetime
from pathlib import Path

# Add the project root to the Python path
import sys
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from universal_recon.plugins.realtor_directory_plugin import scrape_realtor_directory

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/automation_scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def run_weekly_scrape():
    """Execute the weekly realtor directory scrape."""
    logger.info("Starting scheduled realtor directory scrape")
    
    try:
        # Create timestamped output filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"realtor_leads_{timestamp}.csv"
        output_path = os.path.join("outputs", output_filename)
        
        # Run the scraper
        result = scrape_realtor_directory(
            output_path=output_path,
            max_records=None,  # No limit for scheduled runs
            verbose=True
        )
        
        if result['success']:
            logger.info(f"✅ Weekly scrape completed successfully")
            logger.info(f"📁 {result['leads_count']} leads saved to {result['output_path']}")
            
            # Create a symlink to the latest file for easy access
            latest_path = os.path.join("outputs", "realtor_leads_latest.csv")
            if os.path.exists(latest_path):
                os.remove(latest_path)
            
            # For Windows, use copy instead of symlink if not running as admin
            try:
                os.symlink(result['output_path'], latest_path)
            except OSError:
                import shutil
                shutil.copy2(result['output_path'], latest_path)
                logger.info(f"📎 Latest file copied to {latest_path}")
            
        else:
            logger.error(f"❌ Weekly scrape failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        logger.error(f"❌ Scheduler error: {e}")


def run_interactive_mode():
    """Run the scraper in interactive mode with user selections."""
    print("🏠 Realtor Directory Lead Extractor")
    print("=" * 40)
    
    # Get user preferences
    max_records = input("Enter max records to scrape (or press Enter for no limit): ").strip()
    max_records = int(max_records) if max_records.isdigit() else None
    
    # Search parameters
    print("\nOptional search parameters (press Enter to skip):")
    state = input("State (e.g., 'CA', 'NY'): ").strip()
    city = input("City: ").strip()
    specialty = input("Specialty: ").strip()
    
    search_params = {}
    if state:
        search_params['state'] = state
    if city:
        search_params['city'] = city
    if specialty:
        search_params['specialty'] = specialty
    
    # Google Sheets integration
    google_sheet_id = input("Google Sheets ID (optional): ").strip()
    google_sheet_id = google_sheet_id if google_sheet_id else None
    
    # Create output filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"realtor_leads_interactive_{timestamp}.csv"
    output_path = os.path.join("outputs", output_filename)
    
    print(f"\n🚀 Starting scrape...")
    print(f"📁 Output will be saved to: {output_path}")
    
    try:
        result = scrape_realtor_directory(
            output_path=output_path,
            max_records=max_records,
            search_params=search_params if search_params else None,
            google_sheet_id=google_sheet_id,
            verbose=True
        )
        
        if result['success']:
            print(f"\n✅ Scrape completed successfully!")
            print(f"📊 Found {result['leads_count']} leads")
            print(f"📁 Saved to: {result['output_path']}")
        else:
            print(f"\n❌ Scrape failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")


def main():
    """Main function to handle different execution modes."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Realtor Directory Automation")
    parser.add_argument(
        "--mode", 
        choices=["schedule", "interactive", "once"], 
        default="once",
        help="Execution mode: schedule (run scheduler), interactive (user input), once (single run)"
    )
    parser.add_argument("--max-records", type=int, help="Maximum records to scrape")
    parser.add_argument("--output", help="Custom output file path")
    parser.add_argument("--google-sheet-id", help="Google Sheets ID for upload")
    
    args = parser.parse_args()
    
    # Ensure required directories exist
    os.makedirs("outputs", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    if args.mode == "schedule":
        print("🕐 Starting realtor directory automation scheduler")
        print("📅 Scheduled to run every Monday at 8:00 AM")
        
        # Schedule the job for every Monday at 8:00 AM
        schedule.every().monday.at("08:00").do(run_weekly_scrape)
        
        logger.info("Scheduler started - waiting for scheduled time...")
        
        # Keep the script running
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
            
    elif args.mode == "interactive":
        run_interactive_mode()
        
    else:  # once mode
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = args.output or os.path.join("outputs", f"realtor_leads_{timestamp}.csv")
        
        result = scrape_realtor_directory(
            output_path=output_path,
            max_records=args.max_records,
            google_sheet_id=args.google_sheet_id,
            verbose=True
        )
        
        if result['success']:
            print(f"✅ Scrape completed: {result['leads_count']} leads saved to {result['output_path']}")
        else:
            print(f"❌ Scrape failed: {result.get('error', 'Unknown error')}")


if __name__ == "__main__":
    main()
