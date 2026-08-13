from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from handlers.helpers import get_user_from_message

async def user_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await get_user_from_message(update, context) or update.effective_user
    chat = update.effective_chat
    text = f"""
<b>User Info</b>

ID: <code>{user.id}</code>
Name: {user.full_name}
Username: @{user.username or 'None'}
Is Bot: {user.is_bot}
Language: {user.language_code or 'Unknown'}
"""
    if chat.type != "private":
        try:
            member = await context.bot.get_chat_member(chat.id, user.id)
            text += f"Status: {member.status}\n"
        except Exception:
            pass
    await update.message.reply_html(text)

async def chat_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    text = f"""
<b>Chat Info</b>

ID: <code>{chat.id}</code>
Title: {chat.title or 'Private'}
Type: {chat.type}
Username: @{chat.username or 'None'}
"""
    if chat.description:
        text += f"Description: {chat.description[:200]}\n"
    await update.message.reply_html(text)

async def id_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await get_user_from_message(update, context) or update.effective_user
    await update.message.reply_html(
        f"User ID: <code>{user.id}</code>\nChat ID: <code>{update.effective_chat.id}</code>"
    )

def get_handlers():
    return [
        CommandHandler("info", user_info),
        CommandHandler("chatinfo", chat_info),
        CommandHandler("id", id_cmd),
    ]
