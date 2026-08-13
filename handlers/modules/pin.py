from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from handlers.utils.helpers import is_admin

async def pin_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return await update.message.reply_text("Only admins.")
    if not update.message.reply_to_message:
        return await update.message.reply_text("Reply to the message you want to pin.")
    try:
        await context.bot.pin_chat_message(
            update.effective_chat.id,
            update.message.reply_to_message.message_id,
            disable_notification=True
        )
        await update.message.reply_text("📌 Message pinned.")
    except Exception as e:
        await update.message.reply_text(f"Failed: {e}")

async def unpin_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return await update.message.reply_text("Only admins.")
    try:
        await context.bot.unpin_chat_message(update.effective_chat.id)
        await update.message.reply_text("📌 Unpinned.")
    except Exception as e:
        await update.message.reply_text(f"Failed: {e}")

async def unpin_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return await update.message.reply_text("Only admins.")
    try:
        await context.bot.unpin_all_chat_messages(update.effective_chat.id)
        await update.message.reply_text("📌 All messages unpinned.")
    except Exception as e:
        await update.message.reply_text(f"Failed: {e}")

def get_handlers():
    return [
        CommandHandler("pin", pin_message),
        CommandHandler("unpin", unpin_message),
        CommandHandler("unpinall", unpin_all),
    ]
