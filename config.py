import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

PRICE_INTERVAL = int(os.getenv("PRICE_INTERVAL", "60"))
