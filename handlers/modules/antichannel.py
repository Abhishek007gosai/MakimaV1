from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
from handlers.helpers import is_admin
from database.mongodb import get_chat_settings, update_chat_settings

async def antichannel_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return await update.message.reply_text("Only admins.")
    settings = await get_chat_settings(update.effective_chat.id)
    new_state = not settings.get("antichannel", False)
    await update_chat_settings(update.effective_chat.id, {"antichannel": new_state})
    await update.message.reply_text(f"Anti-Channel {'enabled' if new_state else 'disabled'}.")

async def check_channel_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or update.effective_chat.type == "private":
        return
    if not update.message.sender_chat:
        return
    if await is_admin(update, context):
        return
    settings = await get_chat_settings(update.effective_chat.id)
    if not settings.get("antichannel", False):
        return
    try:
        await update.message.delete()
    except Exception:
        pass

def get_handlers():
    return [
        CommandHandler("antichannel", antichannel_toggle),
        MessageHandler(filters.ALL & ~filters.COMMAND, check_channel_messages),
    ]
