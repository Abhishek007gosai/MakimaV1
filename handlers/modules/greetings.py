from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, ChatMemberHandler, filters
from handlers.utils.helpers import is_admin
from database.mongodb import greetings, get_chat_settings, update_chat_settings

async def set_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return await update.message.reply_text("Only admins.")
    if not context.args and not update.message.reply_to_message:
        return await update.message.reply_text("Usage: /setwelcome <text> or reply to a message")
    text = " ".join(context.args) if context.args else update.message.reply_to_message.text
    await greetings.update_one(
        {"chat_id": update.effective_chat.id},
        {"$set": {"welcome": text}},
        upsert=True
    )
    await update_chat_settings(update.effective_chat.id, {"welcome_enabled": True})
    await update.message.reply_text("✅ Welcome message set.")

async def set_goodbye(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return await update.message.reply_text("Only admins.")
    if not context.args and not update.message.reply_to_message:
        return await update.message.reply_text("Usage: /setgoodbye <text>")
    text = " ".join(context.args) if context.args else update.message.reply_to_message.text
    await greetings.update_one(
        {"chat_id": update.effective_chat.id},
        {"$set": {"goodbye": text}},
        upsert=True
    )
    await update.message.reply_text("✅ Goodbye message set.")

async def welcome_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return await update.message.reply_text("Only admins.")
    settings = await get_chat_settings(update.effective_chat.id)
    new_state = not settings.get("welcome_enabled", True)
    await update_chat_settings(update.effective_chat.id, {"welcome_enabled": new_state})
    await update.message.reply_text(f"Welcome messages {'enabled' if new_state else 'disabled'}.")

async def on_user_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = update.chat_member
    if result.new_chat_member.status == "member" and result.old_chat_member.status in ("left", "kicked"):
        settings = await get_chat_settings(update.effective_chat.id)
        if not settings.get("welcome_enabled", True):
            return
        doc = await greetings.find_one({"chat_id": update.effective_chat.id})
        text = doc.get("welcome", "Welcome {user} to the group!") if doc else "Welcome {user}!"
        user = result.new_chat_member.user
        text = text.replace("{user}", user.mention_html()).replace("{name}", user.full_name)
        await context.bot.send_message(update.effective_chat.id, text, parse_mode="HTML")

def get_handlers():
    return [
        CommandHandler("setwelcome", set_welcome),
        CommandHandler("setgoodbye", set_goodbye),
        CommandHandler("welcome", welcome_toggle),
        ChatMemberHandler(on_user_join, ChatMemberHandler.CHAT_MEMBER),
    ]
