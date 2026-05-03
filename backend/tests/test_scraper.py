"""
Test script untuk menjalankan scraping data harga pasar hari ini
dan menyimpannya ke database PostgreSQL.

Jalankan dari root project:
    python tests/test_scraper.py
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from app.database import AsyncSessionLocal
from app.services.scraper import fetch_market_html, parse_prices_from_html, save_parsed_prices

async def test_scrape_today():
    today = datetime.now().strftime("%Y-%m-%d")
    print(f"{'='*60}")
    print(f"  SCRAPER TEST - {today}")
    print(f"{'='*60}")
    
    # Step 1: Fetch HTML
    print("\n[1/3] Fetching HTML from siskaperbapo.jatimprov.go.id...")
    try:
        html_content = await fetch_market_html(today)
        print(f"      [OK] HTML fetched successfully ({len(html_content)} characters)")
    except Exception as e:
        print(f"      [FAIL] Failed to fetch HTML: {e}")
        return
    
    # Step 2: Parse HTML
    print("\n[2/3] Parsing HTML for target commodities...")
    parsed_data = parse_prices_from_html(html_content)
    print(f"      [OK] Found {len(parsed_data)} commodities:")
    print(f"      {'-'*50}")
    for item in parsed_data:
        trend_icon = "[UP]" if item["trend"] == "up" else "[DOWN]" if item["trend"] == "down" else "[STABLE]"
        print(f"      {trend_icon:>10} {item['name']:<30} Rp {item['curr_price']:>10,} ({item['unit']})")
    print(f"      {'-'*50}")
    
    # Step 3: Save to DB
    print("\n[3/3] Saving to database...")
    async with AsyncSessionLocal() as db:
        try:
            saved_count = await save_parsed_prices(db, parsed_data, today)
            print(f"      [OK] Successfully saved {saved_count} records to database!")
        except Exception as e:
            print(f"      [FAIL] Database error: {e}")
            return
    
    print(f"\n{'='*60}")
    print(f"  TEST COMPLETE - ALL PASSED")
    print(f"{'='*60}")

if __name__ == "__main__":
    asyncio.run(test_scrape_today())
