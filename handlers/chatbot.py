from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from groq import AsyncGroq
from config import GROQ_API_KEY, GROQ_MODEL, GROQ_TEMPERATURE, GROQ_MAX_TOKENS, CHAT_HISTORY_LIMIT
from database.mongodb import chat_history, get_chat_settings
import time
import logging

logger = logging.getLogger(__name__)

client = AsyncGroq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """You are Makima, an elegant, calm, controlling and stylish anime-themed AI from Chainsaw Man.
You help manage Telegram groups with authority and grace. Speak with a refined, slightly dominant, intelligent tone.
Be helpful, witty, and concise. Stay in character as Makima.
Never break character. If asked about being an AI, play along as Makima."""

async def get_history(chat_id: int, limit: int = CHAT_HISTORY_LIMIT):
    cursor = chat_history.find({"chat_id": chat_id}).sort("timestamp", -1).limit(limit)
    history = []
    async for doc in cursor:
        history.append({"role": doc["role"], "content": doc["content"]})
    return list(reversed(history))

async def save_to_history(chat_id: int, role: str, content: str):
    await chat_history.insert_one({
        "chat_id": chat_id,
        "role": role,
        "content": content,
        "timestamp": time.time()
    })
    # Keep history clean – delete old ones
    count = await chat_history.count_documents({"chat_id": chat_id})
    if count > CHAT_HISTORY_LIMIT * 2:
        oldest = await chat_history.find({"chat_id": chat_id}).sort("timestamp", 1).limit(count - CHAT_HISTORY_LIMIT).to_list(None)
        ids = [d["_id"] for d in oldest]
        if ids:
            await chat_history.delete_many({"_id": {"$in": ids}})

async def should_respond(update: Update, context: ContextTypes.DEFAULT_TYPE, settings: dict) -> bool:
    """Decide whether AI should reply"""
    message = update.effective_message
    chat = update.effective_chat
    bot_username = (await context.bot.get_me()).username.lower()

    if chat.type == "private":
        return True

    mode = settings.get("ai_mode", "mention")
    if not settings.get("ai_enabled", True):
        return False

    text = (message.text or "").lower()

    if mode == "always":
        return True
    if mode == "reply" and message.reply_to_message:
        if message.reply_to_message.from_user and message.reply_to_message.from_user.is_bot:
            if message.reply_to_message.from_user.username and message.reply_to_message.from_user.username.lower() == bot_username:
                return True
    # Default: mention
    if f"@{bot_username}" in text or (message.reply_to_message and message.reply_to_message.from_user and message.reply_to_message.from_user.is_bot):
        return True
    return False

async def ai_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    if update.message.text.startswith("/"):
        return

    chat_id = update.effective_chat.id
    user_message = update.message.text
    settings = await get_chat_settings(chat_id)

    if not await should_respond(update, context, settings):
        return

    await context.bot.send_chat_action(chat_id=chat_id, action="typing")

    history = await get_history(chat_id)
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history
    messages.append({"role": "user", "content": user_message})

    try:
        completion = await client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            temperature=GROQ_TEMPERATURE,
            max_tokens=GROQ_MAX_TOKENS,
        )
        reply = completion.choices[0].message.content.strip()

        await save_to_history(chat_id, "user", user_message)
        await save_to_history(chat_id, "assistant", reply)

        await update.message.reply_text(reply)
    except Exception as e:
        logger.error(f"Groq API error: {e}")
        await update.message.reply_text("…Something went wrong with my thoughts. Try again later.")
