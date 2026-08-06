from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from database.mongodb import users, chats, warnings, notes, filters_col
from config import OWNER_ID

async def bot_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return await update.message.reply_text("Owner only.")
    user_count = await users.count_documents({})
    chat_count = await chats.count_documents({})
    warn_count = await warnings.count_documents({})
    note_count = await notes.count_documents({})
    filter_count = await filters_col.count_documents({})
    text = f"""
<b>📊 Bot Statistics</b>

Users: <code>{user_count}</code>
Chats: <code>{chat_count}</code>
Warnings: <code>{warn_count}</code>
Notes: <code>{note_count}</code>
Filters: <code>{filter_count}</code>
"""
    await update.message.reply_html(text)

async def chat_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    warn_count = await warnings.count_documents({"chat_id": chat_id})
    note_count = await notes.count_documents({"chat_id": chat_id})
    filter_count = await filters_col.count_documents({"chat_id": chat_id})
    text = f"""
<b>📊 Chat Statistics</b>

Warnings issued: <code>{warn_count}</code>
Notes: <code>{note_count}</code>
Filters: <code>{filter_count}</code>
"""
    await update.message.reply_html(text)

def get_handlers():
    return [
        CommandHandler("stats", bot_stats),
        CommandHandler("chatstats", chat_stats),
    ]
