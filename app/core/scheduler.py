import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.database import AsyncSessionLocal
from app.services.scraper import scrape_market_data

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler(timezone="Asia/Jakarta")

async def daily_market_scrape_job():
    today = datetime.now().strftime("%Y-%m-%d")
    logger.info(f"[Scheduler] Starting daily market scrape for {today}...")
    
    async with AsyncSessionLocal() as db:
        try:
            saved_count = await scrape_market_data(db, today)
            logger.info(f"[Scheduler] Successfully scraped {saved_count} commodities for {today}")
        except Exception as e:
            logger.error(f"[Scheduler] Scraping failed for {today}: {str(e)}")

def init_scheduler():
    scheduler.add_job(
        daily_market_scrape_job,
        trigger=CronTrigger(hour=5, minute=0, timezone="Asia/Jakarta"),
        id="daily_market_scrape",
        name="Daily Market Price Scraper",
        replace_existing=True
    )
    scheduler.start()
    logger.info("[Scheduler] APScheduler started. Market scrape scheduled at 05:00 WIB daily.")

def shutdown_scheduler():
    scheduler.shutdown()
    logger.info("[Scheduler] APScheduler shut down.")
