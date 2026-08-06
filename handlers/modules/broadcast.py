from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from config import OWNER_ID
from database.mongodb import chats, users
import asyncio

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return await update.message.reply_text("Owner only.")
    if not context.args and not update.message.reply_to_message:
        return await update.message.reply_text("Usage: /broadcast <message> or reply to a message")
    text = " ".join(context.args) if context.args else update.message.reply_to_message.text_html or update.message.reply_to_message.text

    sent = 0
    failed = 0
    cursor = chats.find({})
    async for chat in cursor:
        try:
            await context.bot.send_message(chat["chat_id"], text, parse_mode="HTML")
            sent += 1
            await asyncio.sleep(0.05)
        except Exception:
            failed += 1
    await update.message.reply_text(f"Broadcast finished.\nSent: {sent}\nFailed: {failed}")

def get_handlers():
    return [
        CommandHandler("broadcast", broadcast),
    ]
