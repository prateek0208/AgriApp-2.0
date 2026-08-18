"""
backend_alerts.py — AgriTech AI Automated Backend WhatsApp Dispatcher
Runs in the background (or triggered on demand) to pull the latest weather
and market prices for all registered subscribers, and sends personalized alerts.

Usage:
  1. Send alerts once now:
     python backend_alerts.py --once
  2. Run as a background loop (runs every 24 hours):
     python backend_alerts.py --loop 24
"""

import sys
import os
import time
import argparse
import logging
import sqlite3
from datetime import datetime
from dotenv import load_dotenv

# Ensure we can import local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environmental variables
load_dotenv(override=True)

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(get_path("logs", "backend_alerts.log"), encoding="utf-8")
    ]
)
logger = logging.getLogger("AgriTechBackend")

# Import our helper engines
try:
    from core.database import get_subscribers
    from engines.weather_service import get_weather_data
    from alerts.whatsapp_alerts import send_whatsapp_alert
except ImportError as e:
    logger.error(f"Failed to import local modules: {e}")
    sys.exit(1)


def get_current_mandi_price(crop: str) -> int:
    """Returns today's modal price for the specified crop (from demo dictionary)."""
    base_prices = {
        "rice": 2183, "wheat": 2275, "maize": 1850, "cotton": 6620,
        "sugarcane": 315, "soybean": 4600, "groundnut": 5850,
        "tomato": 1200, "onion": 1500, "potato": 900,
        "chillies": 8500, "turmeric": 7200, "ginger": 6000,
        "mustard": 5650, "jowar": 3180, "bajra": 2350,
        "arhar": 7000, "moong": 8558, "gram": 5440,
    }
    return base_prices.get(crop.lower().strip(), 3000)


def get_latest_soil_score(phone: str) -> float:
    """Tries to find the farmer's latest soil health score from prediction history."""
    try:
        conn = sqlite3.connect(get_path('data', 'farm_data.db'))
        cursor = conn.cursor()
        # Find latest record matching their subscription location
        cursor.execute('''
            SELECT nitrogen, phosphorus, potassium, ph, rainfall 
            FROM history 
            ORDER BY id DESC LIMIT 1
        ''')
        row = cursor.fetchone()
        conn.close()

        if row:
            n, p, k, ph, rain = row
            ph_score     = max(0, 100 - (abs(6.5 - ph) * 15))
            n_score      = min(100, (n / 250) * 100)
            p_score      = min(100, (p / 250) * 100)
            k_score      = min(100, (k / 250) * 100)
            rain_score   = 100 if 50 <= rain <= 200 else max(0, 100 - abs(rain - 125) / 2)

            health_score = (ph_score * 0.30 + n_score * 0.20 + p_score * 0.20 + k_score * 0.20 + rain_score * 0.10)
            return round(max(0, min(100, health_score)), 1)
    except Exception as e:
        logger.warning(f"Could not calculate soil score for database: {e}")
    
    return 75.0  # Safe default


def dispatch_alerts():
    """Fetches details and dispatches WhatsApp alerts to all active subscribers."""
    logger.info("📢 Starting automated WhatsApp alert dispatch cycle...")
    
    subscribers = get_subscribers()
    if not subscribers:
        logger.info("ℹ️ No active subscribers found in the database. Cycle completed.")
        return

    logger.info(f"👥 Found {len(subscribers)} subscriber(s) to process.")
    
    success_count = 0
    failure_count = 0
    
    for sub in subscribers:
        phone = sub['phone']
        loc = sub['location']
        crop = sub['crop']
        lang = sub.get('lang', 'en')
        
        logger.info(f"🔄 Processing subscriber: {phone} | Location: {loc} | Crop: {crop}...")
        
        # 1. Fetch live weather
        weather = get_weather_data(loc)
        temp = 25.0
        desc = "N/A"
        if weather:
            temp = weather.get("current_temp", 25.0)
            desc = weather.get("current_desc", "N/A")
        else:
            logger.warning(f"⚠️ Weather data could not be fetched for {loc}, using default values.")
            
        # 2. Get latest Mandi Price
        modal_price = get_current_mandi_price(crop)
        
        # 3. Get soil score
        soil_score = get_latest_soil_score(phone)
        
        # 4. Dispatch Alert
        result = send_whatsapp_alert(
            to_number=phone,
            crop=crop,
            modal_price=modal_price,
            weather_temp=temp,
            weather_desc=desc,
            soil_score=soil_score,
            location=loc,
            lang=lang
        )
        
        if result["success"]:
            logger.info(f"✅ Alert sent successfully to {phone}! SID: {result.get('sid', 'N/A')}")
            success_count += 1
        else:
            logger.error(f"❌ Failed to send alert to {phone}: {result['message']}")
            failure_count += 1
            
        # Add slight delay between messages to respect Twilio API rate limits
        time.sleep(1)

    logger.info(
        f"📊 Alert Dispatch Completed. Success: {success_count} | Failures: {failure_count}"
    )


def main():
    parser = argparse.ArgumentParser(
        description="AgriTech AI Automated WhatsApp Alert Dispatcher"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--once", action="store_true",
        help="Run the dispatch cycle once now and exit"
    )
    group.add_argument(
        "--loop", type=float, metavar="HOURS",
        help="Run infinitely in a loop, dispatching alerts every N hours"
    )
    
    args = parser.parse_args()
    
    if args.once:
        dispatch_alerts()
        logger.info("Exiting.")
    elif args.loop:
        interval_seconds = args.loop * 3600
        logger.info(f"⏰ Scheduler started. Running every {args.loop} hours (interval: {interval_seconds}s)")
        
        # Run immediately on start
        dispatch_alerts()
        
        while True:
            logger.info(f"💤 Sleeping for {args.loop} hours...")
            time.sleep(interval_seconds)
            dispatch_alerts()


if __name__ == "__main__":
    main()
