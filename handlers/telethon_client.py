"""
Telethon client for optional advanced features.
On headless hosts (Docker/Koyeb/Railway) we never prompt for phone/code.
- If BOT_TOKEN is set → start as bot (no interactive login)
- Else if a session file already exists → reuse it
- Otherwise → skip Telethon (pure Bot API mode)
"""
import logging
import os
from telethon import TelegramClient
from config import API_ID, API_HASH, BOT_TOKEN

logger = logging.getLogger(__name__)

_client: TelegramClient | None = None
SESSION_NAME = "makima_session"


async def start_telethon() -> TelegramClient | None:
    """Start Telethon without any interactive prompts."""
    global _client

    if not API_ID or not API_HASH:
        logger.warning("API_ID or API_HASH missing – Telethon disabled")
        return None

    try:
        _client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

        # Prefer bot-token auth (works on headless servers, no phone prompt)
        if BOT_TOKEN:
            await _client.start(bot_token=BOT_TOKEN)
            logger.info("Telethon started with bot token")
            return _client

        # Fallback: only if a session was already authorized offline
        session_file = f"{SESSION_NAME}.session"
        if os.path.exists(session_file):
            await _client.connect()
            if await _client.is_user_authorized():
                logger.info("Telethon started from existing session")
                return _client
            await _client.disconnect()

        logger.warning(
            "No BOT_TOKEN and no authorized session – Telethon disabled "
            "(set BOT_TOKEN or create a session offline)"
        )
        _client = None
        return None

    except Exception as e:
        logger.error(f"Failed to start Telethon: {e}")
        if _client:
            try:
                await _client.disconnect()
            except Exception:
                pass
        _client = None
        return None


async def stop_telethon() -> None:
    """Gracefully disconnect Telethon client."""
    global _client
    if _client:
        try:
            if _client.is_connected():
                await _client.disconnect()
            logger.info("Telethon client stopped")
        except Exception as e:
            logger.warning(f"Error stopping Telethon: {e}")
    _client = None
