from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from handlers.helpers import is_admin
from database.mongodb import disabled_commands

async def disable_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return await update.message.reply_text("Only admins.")
    if not context.args:
        return await update.message.reply_text("Usage: /disable <command>")
    cmd = context.args[0].lower().lstrip("/")
    await disabled_commands.update_one(
        {"chat_id": update.effective_chat.id, "command": cmd},
        {"$set": {"command": cmd}},
        upsert=True
    )
    await update.message.reply_text(f"❌ Disabled `/{cmd}`", parse_mode="Markdown")

async def enable_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return await update.message.reply_text("Only admins.")
    if not context.args:
        return await update.message.reply_text("Usage: /enable <command>")
    cmd = context.args[0].lower().lstrip("/")
    result = await disabled_commands.delete_one({"chat_id": update.effective_chat.id, "command": cmd})
    if result.deleted_count:
        await update.message.reply_text(f"✅ Enabled `/{cmd}`", parse_mode="Markdown")
    else:
        await update.message.reply_text("Command was not disabled.")

async def list_disabled(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cursor = disabled_commands.find({"chat_id": update.effective_chat.id})
    cmds = []
    async for doc in cursor:
        cmds.append(f"• /{doc['command']}")
    if not cmds:
        return await update.message.reply_text("No disabled commands.")
    await update.message.reply_text("<b>Disabled commands:</b>\n" + "\n".join(cmds), parse_mode="HTML")

def get_handlers():
    return [
        CommandHandler("disable", disable_cmd),
        CommandHandler("enable", enable_cmd),
        CommandHandler("disabled", list_disabled),
    ]
