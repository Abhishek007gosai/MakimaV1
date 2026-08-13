from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
from handlers.helpers import is_admin
from database.mongodb import filters_col
import re

async def add_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return await update.message.reply_text("Only admins.")
    if len(context.args) < 2:
        return await update.message.reply_text("Usage: /filter <keyword> <reply text>")
    keyword = context.args[0].lower()
    reply = " ".join(context.args[1:])
    chat_id = update.effective_chat.id
    await filters_col.update_one(
        {"chat_id": chat_id, "keyword": keyword},
        {"$set": {"reply": reply}},
        upsert=True
    )
    await update.message.reply_text(f"✅ Filter added for `{keyword}`", parse_mode="Markdown")

async def stop_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return await update.message.reply_text("Only admins.")
    if not context.args:
        return await update.message.reply_text("Usage: /stop <keyword>")
    keyword = context.args[0].lower()
    result = await filters_col.delete_one({"chat_id": update.effective_chat.id, "keyword": keyword})
    if result.deleted_count:
        await update.message.reply_text(f"🗑 Removed filter `{keyword}`", parse_mode="Markdown")
    else:
        await update.message.reply_text("Filter not found.")

async def list_filters(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cursor = filters_col.find({"chat_id": update.effective_chat.id})
    filters_list = []
    async for doc in cursor:
        filters_list.append(f"• `{doc['keyword']}`")
    if not filters_list:
        return await update.message.reply_text("No filters in this chat.")
    await update.message.reply_text("<b>Filters:</b>\n" + "\n".join(filters_list), parse_mode="HTML")

async def check_filters(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text or update.effective_chat.type == "private":
        return
    text = update.message.text.lower()
    cursor = filters_col.find({"chat_id": update.effective_chat.id})
    async for doc in cursor:
        keyword = doc["keyword"]
        if re.search(rf"\b{re.escape(keyword)}\b", text):
            await update.message.reply_text(doc["reply"])
            break

def get_handlers():
    return [
        CommandHandler("filter", add_filter),
        CommandHandler("stop", stop_filter),
        CommandHandler("filters", list_filters),
        MessageHandler(filters.TEXT & ~filters.COMMAND, check_filters),
    ]
