from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
from database.mongodb import karma
from utils.helpers import get_user_from_message

async def karma_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Detect +1 or -1 on reply"""
    if not update.message or not update.message.reply_to_message:
        return
    text = update.message.text.strip()
    if text not in ("+1", "-1", "++", "--"):
        return
    target = update.message.reply_to_message.from_user
    if target.id == update.effective_user.id:
        return await update.message.reply_text("You can't give karma to yourself.")
    change = 1 if text in ("+1", "++") else -1
    chat_id = update.effective_chat.id
    await karma.update_one(
        {"chat_id": chat_id, "user_id": target.id},
        {"$inc": {"points": change}},
        upsert=True
    )
    doc = await karma.find_one({"chat_id": chat_id, "user_id": target.id})
    points = doc["points"]
    await update.message.reply_html(
        f"{'➕' if change > 0 else '➖'} Karma for {target.mention_html()}: <b>{points}</b>"
    )

async def show_karma(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await get_user_from_message(update, context) or update.effective_user
    doc = await karma.find_one({"chat_id": update.effective_chat.id, "user_id": user.id})
    points = doc["points"] if doc else 0
    await update.message.reply_html(f"⭐ Karma of {user.mention_html()}: <b>{points}</b>")

async def karma_top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cursor = karma.find({"chat_id": update.effective_chat.id}).sort("points", -1).limit(10)
    text = "<b>🏆 Karma Leaderboard</b>\n\n"
    i = 1
    async for doc in cursor:
        text += f"{i}. <code>{doc['user_id']}</code> — {doc['points']}\n"
        i += 1
    if i == 1:
        text += "No karma data yet."
    await update.message.reply_html(text)

def get_handlers():
    return [
        CommandHandler("karma", show_karma),
        CommandHandler("topkarma", karma_top),
        MessageHandler(filters.Regex(r"^(\+1|-1|\+\+|--)$") & filters.REPLY, karma_handler),
    ]
