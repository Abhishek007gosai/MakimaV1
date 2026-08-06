from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from database.mongodb import reports
import time

async def report_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("Reply to the message/user you want to report.")
    reported = update.message.reply_to_message.from_user
    reason = " ".join(context.args) if context.args else "No reason given"
    chat = update.effective_chat

    await reports.insert_one({
        "chat_id": chat.id,
        "reported_user": reported.id,
        "reported_by": update.effective_user.id,
        "reason": reason,
        "message_id": update.message.reply_to_message.message_id,
        "timestamp": time.time()
    })

    # Notify admins
    admins = await context.bot.get_chat_administrators(chat.id)
    text = (
        f"🚨 <b>Report</b>\n"
        f"Reported: {reported.mention_html()}\n"
        f"By: {update.effective_user.mention_html()}\n"
        f"Reason: {reason}"
    )
    for adm in admins:
        if not adm.user.is_bot:
            try:
                await context.bot.send_message(adm.user.id, text, parse_mode="HTML")
            except Exception:
                pass
    await update.message.reply_text("✅ Report submitted to admins.")

def get_handlers():
    return [
        CommandHandler("report", report_user),
        CommandHandler("reports", report_user),
    ]
