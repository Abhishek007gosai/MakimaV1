from telegram import Update, ChatPermissions, ChatMember
from telegram.ext import ContextTypes, CommandHandler
from handlers.utils.helpers import is_admin, get_user_from_message, extract_user_and_reason, can_restrict
from database.mongodb import chats
import logging

logger = logging.getLogger(__name__)

async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return await update.message.reply_text("Only admins can use this command.")
    if not await can_restrict(update, context):
        return await update.message.reply_text("I need restrict permissions.")

    user, reason = extract_user_and_reason(update, context)
    if not user and context.args:
        try:
            user = await context.bot.get_chat(int(context.args[0]) if context.args[0].isdigit() else context.args[0])
        except Exception:
            pass
    if not user:
        return await update.message.reply_text("Reply to a user or provide user id/username.")

    try:
        await context.bot.ban_chat_member(update.effective_chat.id, user.id)
        await update.message.reply_text(f"🔨 Banned {user.mention_html()}\nReason: {reason}", parse_mode="HTML")
    except Exception as e:
        await update.message.reply_text(f"Failed to ban: {e}")

async def unban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return await update.message.reply_text("Only admins can use this command.")
    user = await get_user_from_message(update, context)
    if not user:
        return await update.message.reply_text("Reply to a user or provide id/username.")
    try:
        await context.bot.unban_chat_member(update.effective_chat.id, user.id)
        await update.message.reply_text(f"✅ Unbanned {user.mention_html()}", parse_mode="HTML")
    except Exception as e:
        await update.message.reply_text(f"Failed: {e}")

async def kick_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return await update.message.reply_text("Only admins can use this command.")
    user, reason = extract_user_and_reason(update, context)
    if not user:
        return await update.message.reply_text("Reply to a user.")
    try:
        await context.bot.ban_chat_member(update.effective_chat.id, user.id)
        await context.bot.unban_chat_member(update.effective_chat.id, user.id)
        await update.message.reply_text(f"👢 Kicked {user.mention_html()}\nReason: {reason}", parse_mode="HTML")
    except Exception as e:
        await update.message.reply_text(f"Failed: {e}")

async def mute_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return await update.message.reply_text("Only admins can use this command.")
    user, reason = extract_user_and_reason(update, context)
    if not user:
        return await update.message.reply_text("Reply to a user.")
    perms = ChatPermissions(can_send_messages=False)
    try:
        await context.bot.restrict_chat_member(update.effective_chat.id, user.id, permissions=perms)
        await update.message.reply_text(f"🔇 Muted {user.mention_html()}\nReason: {reason}", parse_mode="HTML")
    except Exception as e:
        await update.message.reply_text(f"Failed: {e}")

async def unmute_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return await update.message.reply_text("Only admins can use this command.")
    user = await get_user_from_message(update, context)
    if not user:
        return await update.message.reply_text("Reply to a user.")
    perms = ChatPermissions(
        can_send_messages=True, can_send_media_messages=True,
        can_send_other_messages=True, can_add_web_page_previews=True
    )
    try:
        await context.bot.restrict_chat_member(update.effective_chat.id, user.id, permissions=perms)
        await update.message.reply_text(f"🔊 Unmuted {user.mention_html()}", parse_mode="HTML")
    except Exception as e:
        await update.message.reply_text(f"Failed: {e}")

async def promote_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return await update.message.reply_text("Only admins can use this command.")
    user = await get_user_from_message(update, context)
    if not user:
        return await update.message.reply_text("Reply to a user.")
    try:
        await context.bot.promote_chat_member(
            update.effective_chat.id, user.id,
            can_manage_chat=True, can_delete_messages=True,
            can_manage_video_chats=True, can_restrict_members=True,
            can_promote_members=False, can_change_info=True,
            can_invite_users=True, can_pin_messages=True
        )
        await update.message.reply_text(f"⬆️ Promoted {user.mention_html()}", parse_mode="HTML")
    except Exception as e:
        await update.message.reply_text(f"Failed: {e}")

async def demote_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return await update.message.reply_text("Only admins can use this command.")
    user = await get_user_from_message(update, context)
    if not user:
        return await update.message.reply_text("Reply to a user.")
    try:
        await context.bot.promote_chat_member(
            update.effective_chat.id, user.id,
            can_manage_chat=False, can_delete_messages=False,
            can_manage_video_chats=False, can_restrict_members=False,
            can_promote_members=False, can_change_info=False,
            can_invite_users=False, can_pin_messages=False
        )
        await update.message.reply_text(f"⬇️ Demoted {user.mention_html()}", parse_mode="HTML")
    except Exception as e:
        await update.message.reply_text(f"Failed: {e}")

async def list_admins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admins = await context.bot.get_chat_administrators(update.effective_chat.id)
    text = "<b>Group Admins:</b>\n\n"
    for adm in admins:
        text += f"• {adm.user.mention_html()} ({adm.status})\n"
    await update.message.reply_html(text)

def get_handlers():
    return [
        CommandHandler("ban", ban_user),
        CommandHandler("unban", unban_user),
        CommandHandler("kick", kick_user),
        CommandHandler("mute", mute_user),
        CommandHandler("unmute", unmute_user),
        CommandHandler("promote", promote_user),
        CommandHandler("demote", demote_user),
        CommandHandler("admins", list_admins),
        CommandHandler("adminlist", list_admins),
    ]
