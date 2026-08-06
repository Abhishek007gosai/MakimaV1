from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from utils.helpers import is_admin
from database.mongodb import rules_col

async def set_rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return await update.message.reply_text("Only admins.")
    if not context.args and not update.message.reply_to_message:
        return await update.message.reply_text("Usage: /setrules <text>")
    text = " ".join(context.args) if context.args else update.message.reply_to_message.text
    await rules_col.update_one(
        {"chat_id": update.effective_chat.id},
        {"$set": {"rules": text}},
        upsert=True
    )
    await update.message.reply_text("✅ Rules updated.")

async def show_rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    doc = await rules_col.find_one({"chat_id": update.effective_chat.id})
    if not doc or not doc.get("rules"):
        return await update.message.reply_text("No rules set for this chat.")
    await update.message.reply_html(f"<b>Group Rules:</b>\n\n{doc['rules']}")

async def clear_rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return await update.message.reply_text("Only admins.")
    await rules_col.delete_one({"chat_id": update.effective_chat.id})
    await update.message.reply_text("Rules cleared.")

def get_handlers():
    return [
        CommandHandler("setrules", set_rules),
        CommandHandler("rules", show_rules),
        CommandHandler("clearrules", clear_rules),
    ]
