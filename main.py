import logging
import sys
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from config import BOT_TOKEN, LOG_LEVEL, API_ID, API_HASH
from database.mongodb import init_db
from handlers.start import start, help_command, callback_handler
from handlers.chatbot import ai_message_handler
from handlers.modules import load_all_handlers
from utils.telethon_client import start_telethon, stop_telethon

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

async def post_init(application: Application):
    await init_db()
    logger.info("Database initialized")

    # Start Telethon (api_id + api_hash) if configured
    if API_ID and API_HASH:
        client = await start_telethon()
        if client:
            application.bot_data["telethon"] = client
            logger.info("Telethon client ready (api_id + api_hash)")
    else:
        logger.warning("API_ID / API_HASH not set – running in pure Bot API mode")

async def post_shutdown(application: Application):
    await stop_telethon()

def main():
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN not set in .env")
        sys.exit(1)

    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .build()
    )

    # Core handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(callback_handler))

    # Load all modules
    load_all_handlers(app)

    # AI Chatbot
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_message_handler))

    logger.info("Makima bot is starting...")
    app.run_polling(allowed_updates=["message", "callback_query", "chat_member", "my_chat_member"])

if __name__ == "__main__":
    main()
