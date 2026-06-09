import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set in .env")

ADMIN_IDS_STR = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = [int(admin_id.strip()) for admin_id in ADMIN_IDS_STR.split(",") if admin_id.strip().isdigit()]

DB_URL = os.getenv("DB_URL", "sqlite+aiosqlite:///bot_database.db")

BASE_ADDRESS = "Ростов-на-Дону, ул. Ченцова, 10а"
# Format: (lat, lon)
BASE_COORDS = (47.234394, 39.728956)
