import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_IDS = [int(x) for x in os.getenv("ADMIN_CHAT_ID", "241131840,444443993,406806178,347009930,35319745,1552303318").split(",") if x.strip()]

RUCAPTCHA_API_KEY = os.getenv("RUCAPTCHA_API_KEY")

PROXY_HOST = os.getenv("PROXY_HOST")
PROXY_PORT = int(os.getenv("PROXY_PORT", "8000"))
PROXY_USER = os.getenv("PROXY_USER")
PROXY_PASS = os.getenv("PROXY_PASS")