"""
Batch scraper: mengambil data harga pasar dari tanggal 1 April - 29 April 2026.

Jalankan dari root project:
    python tests/batch_scraper.py
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date, timedelta
from app.database import AsyncSessionLocal
from app.services.scraper import fetch_market_html, parse_prices_from_html, save_parsed_prices

START_DATE = date(2026, 4, 1)
END_DATE = date(2026, 4, 29)

async def batch_scrape():
    total_days = (END_DATE - START_DATE).days + 1
    print(f"{'='*60}")
    print(f"  BATCH SCRAPER: {START_DATE} s/d {END_DATE} ({total_days} hari)")
    print(f"{'='*60}")
    
    success_count = 0
    fail_count = 0
    current = START_DATE
    
    while current <= END_DATE:
        date_str = current.strftime("%Y-%m-%d")
        day_num = (current - START_DATE).days + 1
        
        print(f"\n[{day_num}/{total_days}] {date_str} ", end="")
        
        try:
            html = await fetch_market_html(date_str)
            parsed = parse_prices_from_html(html)
            
            async with AsyncSessionLocal() as db:
                saved = await save_parsed_prices(db, parsed, date_str)
            
            print(f"-> {saved} komoditas tersimpan [OK]")
            success_count += 1
        except Exception as e:
            print(f"-> GAGAL: {e}")
            fail_count += 1
        
        # Delay 1 detik agar tidak membebani server Jatimprov
        await asyncio.sleep(1)
        current += timedelta(days=1)
    
    print(f"\n{'='*60}")
    print(f"  SELESAI: {success_count} berhasil, {fail_count} gagal")
    print(f"{'='*60}")

if __name__ == "__main__":
    asyncio.run(batch_scrape())
