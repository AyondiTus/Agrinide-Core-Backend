import httpx
from bs4 import BeautifulSoup
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.repositories.market import get_or_create_market_price, upsert_market_price_daily

TARGET_COMMODITIES = {
    "beras premium",
    "beras medium",
    "kedelai lokal",
    "cabe merah keriting",
    "cabe merah besar",
    "cabe rawit merah",
    "bawang merah",
    "bawang putih sinco/honan",
    "kacang hijau",
    "kacang tanah",
    "ketela pohon",
    "kol/kubis",
    "kentang",
    "tomat merah",
    "wortel",
    "buncis"
}

def slugify(text: str) -> str:
    return text.lower().replace(" ", "_").replace("/", "_").replace("-", "_")

async def fetch_market_html(date_str: str) -> str:
    url = "https://siskaperbapo.jatimprov.go.id/harga/tabel.nodesign/"
    headers = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "origin": "https://siskaperbapo.jatimprov.go.id",
        "priority": "u=1, i",
        "referer": "https://siskaperbapo.jatimprov.go.id/harga/tabel",
        "sec-ch-ua": "\"Google Chrome\";v=\"147\", \"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"147\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
        "x-requested-with": "XMLHttpRequest"
    }
    data = {
        "tanggal": date_str,
        "kabkota": ""
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, data=data)
        response.raise_for_status()
        return response.text

def parse_prices_from_html(html_content: str) -> list[dict]:
    soup = BeautifulSoup(html_content, "html.parser")
    rows = soup.find_all("tr")
    
    parsed_data = []
    
    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 7:
            continue
            
        span = cols[1].find("span", class_="price-tooltip-enabled")
        if not span:
            continue
            
        name = span.text.strip()
        name_lower = name.lower()
        
        if name_lower not in TARGET_COMMODITIES:
            continue
            
        unit = cols[2].text.strip()
        
        def parse_price(text: str) -> int:
            cleaned = text.strip().replace('.', '')
            try:
                return int(cleaned) if cleaned else 0
            except ValueError:
                return 0
                
        prev_price = parse_price(cols[3].text)
        curr_price = parse_price(cols[4].text)
        change_rp = parse_price(cols[5].text)
        
        pct_text = cols[6].text.strip().split('%')[0].replace(',', '.').strip()
        try:
            change_pct = float(pct_text) if pct_text else 0.0
        except ValueError:
            change_pct = 0.0
            
        trend_icon = cols[6].find("span")
        trend = "stable"
        if trend_icon:
            classes = trend_icon.get("class", [])
            if "glyphicon-chevron-up" in classes:
                trend = "up"
            elif "glyphicon-chevron-down" in classes:
                trend = "down"
                
        market_price_id = slugify(name)
        
        parsed_data.append({
            "market_price_id": market_price_id,
            "name": name,
            "unit": unit,
            "curr_price": curr_price,
            "prev_price": prev_price,
            "change_rp": change_rp,
            "change_pct": change_pct,
            "trend": trend
        })
        
    return parsed_data

async def save_parsed_prices(db: AsyncSession, parsed_data: list[dict], date_str: str) -> int:
    date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
    saved_count = 0
    
    for item in parsed_data:
        # 1. Upsert MarketPrice (induk)
        mp = await get_or_create_market_price(
            db, 
            item["market_price_id"], 
            item["name"], 
            item["unit"]
        )
            
        # 2. Insert MarketPriceDaily (histori)
        await upsert_market_price_daily(
            db=db,
            market_price_id=item["market_price_id"],
            date_obj=date_obj,
            current_price=item["curr_price"],
            previous_price=item["prev_price"],
            change_rp=item["change_rp"],
            change_percentage=item["change_pct"],
            trend=item["trend"]
        )
            
        saved_count += 1
        
    await db.commit()
    return saved_count

async def scrape_market_data(db: AsyncSession, date_str: str) -> int:
    html_content = await fetch_market_html(date_str)
    parsed_data = parse_prices_from_html(html_content)
    return await save_parsed_prices(db, parsed_data, date_str)
