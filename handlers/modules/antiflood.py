from telegram import Update, ChatPermissions
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
from handlers.utils.helpers import is_admin, is_approved
from database.mongodb import get_chat_settings, update_chat_settings
from collections import defaultdict
import time

# In-memory flood tracker (for production consider Redis)
flood_tracker = defaultdict(list)

async def antiflood_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return await update.message.reply_text("Only admins.")
    settings = await get_chat_settings(update.effective_chat.id)
    new_state = not settings.get("antiflood", True)
    await update_chat_settings(update.effective_chat.id, {"antiflood": new_state})
    await update.message.reply_text(f"Antiflood {'enabled' if new_state else 'disabled'}.")

async def set_flood_limit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return await update.message.reply_text("Only admins.")
    if not context.args or not context.args[0].isdigit():
        return await update.message.reply_text("Usage: /setflood <number>")
    limit = int(context.args[0])
    await update_chat_settings(update.effective_chat.id, {"antiflood_limit": limit})
    await update.message.reply_text(f"Flood limit set to {limit} messages.")

async def check_flood(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or update.effective_chat.type == "private":
        return
    if await is_admin(update, context):
        return
    if await is_approved(update.effective_chat.id, update.effective_user.id):
        return

    settings = await get_chat_settings(update.effective_chat.id)
    if not settings.get("antiflood", True):
        return

    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    limit = settings.get("antiflood_limit", 5)
    window = 10  # seconds

    key = (chat_id, user_id)
    now = time.time()
    flood_tracker[key] = [t for t in flood_tracker[key] if now - t < window]
    flood_tracker[key].append(now)

    if len(flood_tracker[key]) > limit:
        try:
            perms = ChatPermissions(can_send_messages=False)
            await context.bot.restrict_chat_member(chat_id, user_id, permissions=perms)
            await update.message.reply_text(
                f"🌊 {update.effective_user.mention_html()} muted for flooding.",
                parse_mode="HTML"
            )
            flood_tracker[key].clear()
        except Exception:
            pass

def get_handlers():
    return [
        CommandHandler("antiflood", antiflood_toggle),
        CommandHandler("setflood", set_flood_limit),
        MessageHandler(filters.ALL & ~filters.COMMAND & ~filters.StatusUpdate.ALL, check_flood),
    ]
