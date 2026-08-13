from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
from handlers.helpers import is_admin, is_approved
from database.mongodb import blacklist
import re

async def add_blocklist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return await update.message.reply_text("Only admins.")
    if not context.args:
        return await update.message.reply_text("Usage: /addblocklist <word>")
    word = " ".join(context.args).lower()
    await blacklist.update_one(
        {"chat_id": update.effective_chat.id, "word": word},
        {"$set": {"word": word}},
        upsert=True
    )
    await update.message.reply_text(f"🚫 Added `{word}` to blocklist.", parse_mode="Markdown")

async def rm_blocklist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return await update.message.reply_text("Only admins.")
    if not context.args:
        return await update.message.reply_text("Usage: /rmblocklist <word>")
    word = " ".join(context.args).lower()
    result = await blacklist.delete_one({"chat_id": update.effective_chat.id, "word": word})
    if result.deleted_count:
        await update.message.reply_text(f"Removed `{word}` from blocklist.", parse_mode="Markdown")
    else:
        await update.message.reply_text("Word not found.")

async def list_blocklist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cursor = blacklist.find({"chat_id": update.effective_chat.id})
    words = []
    async for doc in cursor:
        words.append(f"• `{doc['word']}`")
    if not words:
        return await update.message.reply_text("Blocklist is empty.")
    await update.message.reply_text("<b>Blocklist:</b>\n" + "\n".join(words), parse_mode="HTML")

async def check_blocklist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text or update.effective_chat.type == "private":
        return
    if await is_admin(update, context) or await is_approved(update.effective_chat.id, update.effective_user.id):
        return
    text = update.message.text.lower()
    cursor = blacklist.find({"chat_id": update.effective_chat.id})
    async for doc in cursor:
        if re.search(rf"\b{re.escape(doc['word'])}\b", text):
            try:
                await update.message.delete()
                await update.message.reply_text(
                    f"🚫 {update.effective_user.mention_html()} used a blocked word.",
                    parse_mode="HTML"
                )
            except Exception:
                pass
            break

def get_handlers():
    return [
        CommandHandler("addblocklist", add_blocklist),
        CommandHandler("rmblocklist", rm_blocklist),
        CommandHandler("blocklist", list_blocklist),
        MessageHandler(filters.TEXT & ~filters.COMMAND, check_blocklist),
    ]
