from telegram import Update, ChatMember
from telegram.ext import ContextTypes
from config import OWNER_ID
from database.mongodb import approvals

async def is_owner(user_id: int) -> bool:
    return user_id == OWNER_ID

async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int = None) -> bool:
    if user_id is None:
        user_id = update.effective_user.id
    if await is_owner(user_id):
        return True
    chat = update.effective_chat
    if chat.type == "private":
        return False
    try:
        member = await context.bot.get_chat_member(chat.id, user_id)
        return member.status in (ChatMember.ADMINISTRATOR, ChatMember.OWNER)
    except Exception:
        return False

async def is_approved(chat_id: int, user_id: int) -> bool:
    doc = await approvals.find_one({"chat_id": chat_id, "user_id": user_id})
    return bool(doc)

async def get_user_from_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Extract target user from reply or command args"""
    message = update.effective_message
    if message.reply_to_message:
        return message.reply_to_message.from_user
    if context.args:
        arg = context.args[0]
        if arg.startswith("@"):
            try:
                user = await context.bot.get_chat(arg)
                return user
            except Exception:
                return None
        try:
            user_id = int(arg)
            user = await context.bot.get_chat(user_id)
            return user
        except Exception:
            return None
    return None

def extract_user_and_reason(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Return (user, reason) from reply or args"""
    message = update.effective_message
    user = None
    reason = "No reason provided"
    args = context.args or []

    if message.reply_to_message:
        user = message.reply_to_message.from_user
        if args:
            reason = " ".join(args)
    elif args:
        # first arg is user, rest is reason
        try:
            if args[0].startswith("@"):
                # will be resolved later
                pass
            else:
                user_id = int(args[0])
                # user will be fetched later
            if len(args) > 1:
                reason = " ".join(args[1:])
        except ValueError:
            reason = " ".join(args)
    return user, reason

async def can_restrict(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Check if bot has permission to restrict members"""
    bot_member = await context.bot.get_chat_member(update.effective_chat.id, context.bot.id)
    return bot_member.can_restrict_members if bot_member.status == ChatMember.ADMINISTRATOR else False
