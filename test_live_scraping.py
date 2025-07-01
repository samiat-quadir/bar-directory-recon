#!/usr/bin/env python3
"""
Phase 2 Live Scraping Test
Test the enhanced live scraping functionality with safety limits
"""

import sys
from pathlib import Path

# Add project path
script_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(script_dir))

# Import after path setup
from tools.realtor_directory_scraper import scrape_realtor_directory  # noqa: E402


def test_live_scraping_limited() -> None:
    """Test live scraping with very limited records to be respectful"""
    print("🔴 Testing Phase 2 Live Scraping (Limited)")
    print("=" * 50)
    print("⚠️  This test will attempt real scraping with a 3-record limit")
    print("   to be respectful to target websites.")
    print()
    
    try:
        # Test with minimal records and debug enabled
        output_file = scrape_realtor_directory(
            max_records=3,  # Very limited for testing
            debug=True,
            use_selenium=True,
            test_mode=False  # Real live mode
        )
        
        if output_file:
            print(f"\n✅ Live test successful: {output_file}")
            
            # Read and display results
            import pandas as pd
            df = pd.read_csv(output_file)
            print(f"\n📊 Results ({len(df)} records):")
            print(df.to_string(index=False))
            
        else:
            print("\n⚠️  Live test returned no file (likely fell back to test mode)")
            
    except Exception as e:
        print(f"\n❌ Live test failed: {e}")
        print("   This is expected if sites are unavailable or block requests")


if __name__ == "__main__":
    test_live_scraping_limited()
