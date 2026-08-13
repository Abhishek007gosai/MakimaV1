import logging
from telethon import TelegramClient
from config import API_ID, API_HASH

logger = logging.getLogger(__name__)

_client: TelegramClient | None = None


async def start_telethon() -> TelegramClient | None:
    """Start Telethon client if API_ID + API_HASH are configured."""
    global _client

    if not API_ID or not API_HASH:
        logger.warning("API_ID or API_HASH missing – Telethon disabled")
        return None

    try:
        _client = TelegramClient(
            "makima_session",
            API_ID,
            API_HASH,
        )
        await _client.start()
        logger.info("Telethon client started")
        return _client
    except Exception as e:
        logger.error(f"Failed to start Telethon: {e}")
        _client = None
        return None


async def stop_telethon() -> None:
    """Gracefully disconnect Telethon client."""
    global _client
    if _client and _client.is_connected():
        await _client.disconnect()
        logger.info("Telethon client stopped")
    _client = None
