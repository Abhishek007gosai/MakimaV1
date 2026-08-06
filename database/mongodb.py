from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URI, MONGO_DB
import logging

logger = logging.getLogger(__name__)

client = AsyncIOMotorClient(MONGO_URI)
db = client[MONGO_DB]

# Collections
users = db.users
chats = db.chats
warnings = db.warnings
notes = db.notes
filters_col = db.filters
blacklist = db.blacklist
settings = db.settings
chat_history = db.chat_history
approvals = db.approvals
federations = db.federations
karma = db.karma
reports = db.reports
locks = db.locks
disabled_commands = db.disabled_commands
greetings = db.greetings
rules_col = db.rules
stats = db.stats

async def init_db():
    """Create indexes for better performance"""
    try:
        await users.create_index("user_id", unique=True)
        await chats.create_index("chat_id", unique=True)
        await warnings.create_index([("chat_id", 1), ("user_id", 1)])
        await notes.create_index([("chat_id", 1), ("name", 1)])
        await filters_col.create_index([("chat_id", 1), ("keyword", 1)])
        await blacklist.create_index([("chat_id", 1), ("word", 1)])
        await chat_history.create_index([("chat_id", 1), ("timestamp", -1)])
        await karma.create_index([("chat_id", 1), ("user_id", 1)])
        await locks.create_index("chat_id", unique=True)
        await disabled_commands.create_index([("chat_id", 1), ("command", 1)])
        await greetings.create_index("chat_id", unique=True)
        await rules_col.create_index("chat_id", unique=True)
        logger.info("MongoDB indexes created successfully")
    except Exception as e:
        logger.error(f"Error creating indexes: {e}")

async def get_chat_settings(chat_id: int) -> dict:
    doc = await settings.find_one({"chat_id": chat_id})
    if not doc:
        default = {
            "chat_id": chat_id,
            "welcome_enabled": True,
            "goodbye_enabled": False,
            "antiflood": True,
            "antiflood_limit": 5,
            "warn_limit": 3,
            "night_mode": False,
            "nsfw_filter": False,
            "ai_enabled": True,
            "ai_mode": "mention",  # mention | always | reply
        }
        await settings.insert_one(default)
        return default
    return doc

async def update_chat_settings(chat_id: int, data: dict):
    await settings.update_one(
        {"chat_id": chat_id},
        {"$set": data},
        upsert=True
    )
