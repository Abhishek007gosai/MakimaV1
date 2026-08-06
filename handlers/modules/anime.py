from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
import random

QUOTES = [
    "The future is not a straight line. It is filled with many crossroads.",
    "Dogs are more honest than humans.",
    "Control is everything.",
    "I want to see the real you.",
]

async def anime_quote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"💬 {random.choice(QUOTES)}")

async def waifu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🌸 Waifu feature – integrate with an anime image API if desired.")

def get_handlers():
    return [
        CommandHandler("quote", anime_quote),
        CommandHandler("anime", anime_quote),
        CommandHandler("waifu", waifu),
    ]
