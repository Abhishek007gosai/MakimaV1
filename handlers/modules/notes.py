from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from handlers.utils.helpers import is_admin
from database.mongodb import notes

async def save_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return await update.message.reply_text("Only admins can save notes.")
    if len(context.args) < 2:
        return await update.message.reply_text("Usage: /save <name> <content>")
    name = context.args[0].lower()
    content = " ".join(context.args[1:])
    # Also support reply
    if update.message.reply_to_message and update.message.reply_to_message.text:
        content = update.message.reply_to_message.text
    await notes.update_one(
        {"chat_id": update.effective_chat.id, "name": name},
        {"$set": {"content": content}},
        upsert=True
    )
    await update.message.reply_text(f"📝 Note `{name}` saved.", parse_mode="Markdown")

async def get_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Usage: /get <name> or #<name>")
    name = context.args[0].lower().lstrip("#")
    doc = await notes.find_one({"chat_id": update.effective_chat.id, "name": name})
    if not doc:
        return await update.message.reply_text("Note not found.")
    await update.message.reply_text(doc["content"])

async def list_notes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cursor = notes.find({"chat_id": update.effective_chat.id})
    names = []
    async for doc in cursor:
        names.append(f"• `{doc['name']}`")
    if not names:
        return await update.message.reply_text("No notes saved.")
    await update.message.reply_text("<b>Notes:</b>\n" + "\n".join(names), parse_mode="HTML")

async def clear_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return await update.message.reply_text("Only admins.")
    if not context.args:
        return await update.message.reply_text("Usage: /clear <name>")
    name = context.args[0].lower()
    result = await notes.delete_one({"chat_id": update.effective_chat.id, "name": name})
    if result.deleted_count:
        await update.message.reply_text(f"🗑 Note `{name}` deleted.", parse_mode="Markdown")
    else:
        await update.message.reply_text("Note not found.")

def get_handlers():
    return [
        CommandHandler("save", save_note),
        CommandHandler("get", get_note),
        CommandHandler("notes", list_notes),
        CommandHandler("clear", clear_note),
    ]
