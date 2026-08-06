from telegram import Update, ChatPermissions
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
from utils.helpers import is_admin
from database.mongodb import locks
import logging

logger = logging.getLogger(__name__)

LOCK_TYPES = {
    "all": "Everything",
    "msg": "Messages",
    "media": "Media",
    "sticker": "Stickers",
    "gif": "GIFs",
    "video": "Videos",
    "voice": "Voice notes",
    "audio": "Audio",
    "document": "Documents",
    "contact": "Contacts",
    "location": "Locations",
    "url": "URLs / Links",
    "forward": "Forwards",
    "game": "Games",
    "anonchannel": "Anonymous channels",
}

async def get_locks(chat_id: int) -> dict:
    doc = await locks.find_one({"chat_id": chat_id})
    return doc.get("locked", {}) if doc else {}

async def set_lock(chat_id: int, lock_type: str, value: bool):
    await locks.update_one(
        {"chat_id": chat_id},
        {"$set": {f"locked.{lock_type}": value}},
        upsert=True
    )

async def lock_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return await update.message.reply_text("Only admins.")
    if not context.args:
        return await update.message.reply_text(
            "Usage: /lock <type>\nTypes: " + ", ".join(LOCK_TYPES.keys())
        )
    lock_type = context.args[0].lower()
    if lock_type not in LOCK_TYPES:
        return await update.message.reply_text("Unknown lock type.")
    await set_lock(update.effective_chat.id, lock_type, True)
    await update.message.reply_text(f"🔒 Locked: {LOCK_TYPES[lock_type]}")

async def unlock_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return await update.message.reply_text("Only admins.")
    if not context.args:
        return await update.message.reply_text("Usage: /unlock <type>")
    lock_type = context.args[0].lower()
    if lock_type not in LOCK_TYPES:
        return await update.message.reply_text("Unknown lock type.")
    await set_lock(update.effective_chat.id, lock_type, False)
    await update.message.reply_text(f"🔓 Unlocked: {LOCK_TYPES[lock_type]}")

async def locks_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    locked = await get_locks(update.effective_chat.id)
    if not locked:
        return await update.message.reply_text("No locks active.")
    text = "<b>Current Locks:</b>\n"
    for k, v in locked.items():
        if v:
            text += f"• {LOCK_TYPES.get(k, k)}\n"
    await update.message.reply_html(text)

async def check_locks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Message handler that deletes locked content"""
    if not update.message or update.effective_chat.type == "private":
        return
    if await is_admin(update, context):
        return  # admins bypass

    locked = await get_locks(update.effective_chat.id)
    if not locked:
        return

    msg = update.message
    should_delete = False

    if locked.get("all"):
        should_delete = True
    elif locked.get("msg") and msg.text:
        should_delete = True
    elif locked.get("sticker") and msg.sticker:
        should_delete = True
    elif locked.get("gif") and msg.animation:
        should_delete = True
    elif locked.get("media") and (msg.photo or msg.video or msg.document or msg.audio or msg.voice):
        should_delete = True
    elif locked.get("video") and msg.video:
        should_delete = True
    elif locked.get("voice") and msg.voice:
        should_delete = True
    elif locked.get("audio") and msg.audio:
        should_delete = True
    elif locked.get("document") and msg.document:
        should_delete = True
    elif locked.get("contact") and msg.contact:
        should_delete = True
    elif locked.get("location") and msg.location:
        should_delete = True
    elif locked.get("forward") and msg.forward_origin:
        should_delete = True
    elif locked.get("url") and msg.entities:
        for ent in msg.entities:
            if ent.type in ("url", "text_link"):
                should_delete = True
                break
    elif locked.get("anonchannel") and msg.sender_chat:
        should_delete = True

    if should_delete:
        try:
            await msg.delete()
        except Exception:
            pass

def get_handlers():
    return [
        CommandHandler("lock", lock_cmd),
        CommandHandler("unlock", unlock_cmd),
        CommandHandler("locks", locks_cmd),
        MessageHandler(filters.ALL & ~filters.COMMAND & ~filters.StatusUpdate.ALL, check_locks),
    ]
