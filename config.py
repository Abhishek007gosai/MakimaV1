import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_ID = int(os.getenv("API_ID", ""))
API_HASH = os.getenv("API_HASH", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "makima_bot")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

# Groq settings
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_TEMPERATURE = 0.7
GROQ_MAX_TOKENS = 1024

# Bot settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
MAX_WARNINGS = 3
ANTIFLOOD_LIMIT = 5
ANTIFLOOD_TIME = 10  # seconds
CHAT_HISTORY_LIMIT = 12

# Support / Updates channels (customize)
SUPPORT_CHAT = "https://t.me/your_support"
UPDATES_CHANNEL = "https://t.me/your_updates"
