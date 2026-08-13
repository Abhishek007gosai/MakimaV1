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


async def _safe_create_index(collection, keys, **kwargs):
    """Create an index, logging but not raising on failure."""
    try:
        await collection.create_index(keys, **kwargs)
    except Exception as e:
        # Index already exists or conflict with existing data – non-fatal
        logger.warning(f"Index on {collection.name} {keys}: {e}")


async def init_db():
    """Create indexes for better performance. Cleans null keys that block unique indexes."""
    try:
        # Remove documents with null/missing user_id that block the unique index
        result = await users.delete_many({"$or": [{"user_id": None}, {"user_id": {"$exists": False}}]})
        if result.deleted_count:
            logger.info(f"Cleaned {result.deleted_count} users documents with null user_id")

        result = await chats.delete_many({"$or": [{"chat_id": None}, {"chat_id": {"$exists": False}}]})
        if result.deleted_count:
            logger.info(f"Cleaned {result.deleted_count} chats documents with null chat_id")

        # Create indexes one-by-one so a single failure doesn't skip the rest
        await _safe_create_index(users, "user_id", unique=True)
        await _safe_create_index(chats, "chat_id", unique=True)
        await _safe_create_index(warnings, [("chat_id", 1), ("user_id", 1)])
        await _safe_create_index(notes, [("chat_id", 1), ("name", 1)])
        await _safe_create_index(filters_col, [("chat_id", 1), ("keyword", 1)])
        await _safe_create_index(blacklist, [("chat_id", 1), ("word", 1)])
        await _safe_create_index(chat_history, [("chat_id", 1), ("timestamp", -1)])
        await _safe_create_index(karma, [("chat_id", 1), ("user_id", 1)])
        await _safe_create_index(locks, "chat_id", unique=True)
        await _safe_create_index(disabled_commands, [("chat_id", 1), ("command", 1)])
        await _safe_create_index(greetings, "chat_id", unique=True)
        await _safe_create_index(rules_col, "chat_id", unique=True)

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
