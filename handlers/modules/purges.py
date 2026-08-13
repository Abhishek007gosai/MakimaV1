from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from handlers.helpers import is_admin
import asyncio

async def purge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return await update.message.reply_text("Only admins.")
    if not update.message.reply_to_message:
        return await update.message.reply_text("Reply to the starting message to purge from.")

    chat_id = update.effective_chat.id
    start_id = update.message.reply_to_message.message_id
    end_id = update.message.message_id

    deleted = 0
    for msg_id in range(start_id, end_id + 1):
        try:
            await context.bot.delete_message(chat_id, msg_id)
            deleted += 1
            await asyncio.sleep(0.05)  # rate limit protection
        except Exception:
            pass
    # Delete the command message too if possible
    try:
        await update.message.delete()
    except Exception:
        pass
    status = await context.bot.send_message(chat_id, f"🧹 Purged {deleted} messages.")
    await asyncio.sleep(3)
    try:
        await status.delete()
    except Exception:
        pass

async def del_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return await update.message.reply_text("Only admins.")
    if not update.message.reply_to_message:
        return await update.message.reply_text("Reply to a message to delete it.")
    try:
        await update.message.reply_to_message.delete()
        await update.message.delete()
    except Exception as e:
        await update.message.reply_text(f"Failed: {e}")

def get_handlers():
    return [
        CommandHandler("purge", purge),
        CommandHandler("del", del_message),
        CommandHandler("spurge", purge),  # silent variant can be same for now
    ]
