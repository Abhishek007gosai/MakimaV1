from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from handlers.utils.helpers import is_admin
import time

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start = time.time()
    msg = await update.message.reply_text("Pong!")
    end = time.time()
    await msg.edit_text(f"Pong! `{round((end - start) * 1000, 2)} ms`", parse_mode="Markdown")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Usage: /echo <text>")
    await update.message.reply_text(" ".join(context.args))

async def say(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return
    if not context.args:
        return await update.message.reply_text("Usage: /say <text>")
    try:
        await update.message.delete()
    except Exception:
        pass
    await context.bot.send_message(update.effective_chat.id, " ".join(context.args))

def get_handlers():
    return [
        CommandHandler("ping", ping),
        CommandHandler("echo", echo),
        CommandHandler("say", say),
    ]
