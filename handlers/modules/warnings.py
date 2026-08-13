from telegram import Update, ChatPermissions
from telegram.ext import ContextTypes, CommandHandler
from handlers.helpers import is_admin, get_user_from_message, extract_user_and_reason
from database.mongodb import warnings, get_chat_settings, update_chat_settings
from config import MAX_WARNINGS
import time

async def warn_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return await update.message.reply_text("Only admins can warn users.")
    user, reason = extract_user_and_reason(update, context)
    if not user:
        return await update.message.reply_text("Reply to a user or provide id.")
    chat_id = update.effective_chat.id
    settings = await get_chat_settings(chat_id)
    limit = settings.get("warn_limit", MAX_WARNINGS)

    # Increment warning
    doc = await warnings.find_one({"chat_id": chat_id, "user_id": user.id})
    count = (doc["count"] if doc else 0) + 1
    await warnings.update_one(
        {"chat_id": chat_id, "user_id": user.id},
        {"$set": {"count": count, "last_reason": reason, "last_warn": time.time()}},
        upsert=True
    )

    text = f"⚠️ {user.mention_html()} has been warned ({count}/{limit})\nReason: {reason}"
    if count >= limit:
        # Auto mute or ban
        perms = ChatPermissions(can_send_messages=False)
        try:
            await context.bot.restrict_chat_member(chat_id, user.id, permissions=perms)
            text += f"\n\n🔇 User has reached the warn limit and has been muted."
            await warnings.update_one({"chat_id": chat_id, "user_id": user.id}, {"$set": {"count": 0}})
        except Exception:
            text += "\n\n(Could not auto-mute – check my permissions)"
    await update.message.reply_html(text)

async def unwarn_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return await update.message.reply_text("Only admins.")
    user = await get_user_from_message(update, context)
    if not user:
        return await update.message.reply_text("Reply to a user.")
    chat_id = update.effective_chat.id
    doc = await warnings.find_one({"chat_id": chat_id, "user_id": user.id})
    if not doc or doc["count"] <= 0:
        return await update.message.reply_text("User has no warnings.")
    new_count = doc["count"] - 1
    await warnings.update_one(
        {"chat_id": chat_id, "user_id": user.id},
        {"$set": {"count": new_count}}
    )
    await update.message.reply_html(f"✅ Removed one warning from {user.mention_html()}. Now {new_count} warnings.")

async def warns(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await get_user_from_message(update, context) or update.effective_user
    chat_id = update.effective_chat.id
    doc = await warnings.find_one({"chat_id": chat_id, "user_id": user.id})
    count = doc["count"] if doc else 0
    reason = doc.get("last_reason", "—") if doc else "—"
    await update.message.reply_html(
        f"⚠️ Warnings for {user.mention_html()}: <b>{count}</b>\nLast reason: {reason}"
    )

async def resetwarns(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return await update.message.reply_text("Only admins.")
    user = await get_user_from_message(update, context)
    if not user:
        return await update.message.reply_text("Reply to a user.")
    await warnings.delete_one({"chat_id": update.effective_chat.id, "user_id": user.id})
    await update.message.reply_html(f"✅ Warnings reset for {user.mention_html()}.")

async def set_warn_limit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return await update.message.reply_text("Only admins.")
    if not context.args or not context.args[0].isdigit():
        return await update.message.reply_text("Usage: /warnlimit <number>")
    limit = int(context.args[0])
    await update_chat_settings(update.effective_chat.id, {"warn_limit": limit})
    await update.message.reply_text(f"Warn limit set to {limit}.")

def get_handlers():
    return [
        CommandHandler("warn", warn_user),
        CommandHandler("unwarn", unwarn_user),
        CommandHandler("warns", warns),
        CommandHandler("resetwarns", resetwarns),
        CommandHandler("warnlimit", set_warn_limit),
    ]
