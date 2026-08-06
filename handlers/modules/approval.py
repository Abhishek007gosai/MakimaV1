from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from utils.helpers import is_admin, get_user_from_message
from database.mongodb import approvals

async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return await update.message.reply_text("Only admins.")
    user = await get_user_from_message(update, context)
    if not user:
        return await update.message.reply_text("Reply to a user.")
    await approvals.update_one(
        {"chat_id": update.effective_chat.id, "user_id": user.id},
        {"$set": {"approved": True}},
        upsert=True
    )
    await update.message.reply_html(f"✅ Approved {user.mention_html()}")

async def unapprove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return await update.message.reply_text("Only admins.")
    user = await get_user_from_message(update, context)
    if not user:
        return await update.message.reply_text("Reply to a user.")
    await approvals.delete_one({"chat_id": update.effective_chat.id, "user_id": user.id})
    await update.message.reply_html(f"❌ Unapproved {user.mention_html()}")

async def list_approved(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cursor = approvals.find({"chat_id": update.effective_chat.id})
    users = []
    async for doc in cursor:
        users.append(f"• <code>{doc['user_id']}</code>")
    if not users:
        return await update.message.reply_text("No approved users.")
    await update.message.reply_html("<b>Approved users:</b>\n" + "\n".join(users))

def get_handlers():
    return [
        CommandHandler("approve", approve),
        CommandHandler("unapprove", unapprove),
        CommandHandler("approved", list_approved),
    ]
