from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
import random

SLAPS = [
    "{user} slapped {target} with a large trout!",
    "{user} slapped {target} around a bit with a large trout.",
    "{user} gives {target} a well-deserved slap.",
]

HUGS = [
    "{user} hugs {target} tightly!",
    "{user} gives {target} a warm hug.",
]

PATS = [
    "{user} pats {target} on the head.",
    "{user} gently pats {target}.",
]

RUNS = [
    "Runs away screaming!",
    "Teleports behind you.",
    "Dashes into the sunset.",
]

async def slap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = "someone"
    if update.message.reply_to_message:
        target = update.message.reply_to_message.from_user.mention_html()
    elif context.args:
        target = context.args[0]
    text = random.choice(SLAPS).format(
        user=update.effective_user.mention_html(),
        target=target
    )
    await update.message.reply_html(text)

async def hug(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = "someone"
    if update.message.reply_to_message:
        target = update.message.reply_to_message.from_user.mention_html()
    text = random.choice(HUGS).format(
        user=update.effective_user.mention_html(),
        target=target
    )
    await update.message.reply_html(text)

async def pat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = "someone"
    if update.message.reply_to_message:
        target = update.message.reply_to_message.from_user.mention_html()
    text = random.choice(PATS).format(
        user=update.effective_user.mention_html(),
        target=target
    )
    await update.message.reply_html(text)

async def runs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(random.choice(RUNS))

async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🎲 You rolled: {random.randint(1, 6)}")

def get_handlers():
    return [
        CommandHandler("slap", slap),
        CommandHandler("hug", hug),
        CommandHandler("pat", pat),
        CommandHandler("runs", runs),
        CommandHandler("roll", roll),
    ]
