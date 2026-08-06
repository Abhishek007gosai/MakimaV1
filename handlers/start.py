from telegram import Update, InputMediaPhoto
from telegram.ext import ContextTypes
from utils.keyboards import main_menu, modules_keyboard, category_keyboard, back_button
from database.mongodb import users, chats
import logging

logger = logging.getLogger(__name__)

WELCOME_TEXT = """
Hello there, I'm <b>Makima</b> 🦋

I've got lots of features like <b>AI Chatbot</b>, Anime, Notes, Filters, Fun and many other useful commands!
Tap a category below to browse what I can do.
"""

GROUP_WELCOME = """
Hey {user}, I'm <b>Makima</b>!

An anime-themed group management bot created for elegance, control, and style.

👉 Click the buttons below to explore my powers.
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat

    # Save / update user
    await users.update_one(
        {"user_id": user.id},
        {"$set": {
            "user_id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "last_seen": update.message.date if update.message else None
        }},
        upsert=True
    )

    if chat.type == "private":
        await update.message.reply_html(
            WELCOME_TEXT,
            reply_markup=main_menu()
        )
    else:
        # In group
        await chats.update_one(
            {"chat_id": chat.id},
            {"$set": {
                "chat_id": chat.id,
                "title": chat.title,
                "type": chat.type,
            }},
            upsert=True
        )
        text = GROUP_WELCOME.format(user=user.mention_html())
        await update.message.reply_html(text, reply_markup=main_menu())


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
<b>Makima Bot – Help</b>

I am a powerful group management bot with AI chatbot powered by Groq.

<b>Main Categories:</b>
• Admin – Ban, mute, promote, etc.
• Anti-Spam / Antiflood / Anti-Channel
• Filters, Notes, Greetings, Rules
• Locks, Warnings, Reports
• Fun, Karma, Rankings, Memes
• AI Chatbot (mention me or reply)
• And many more...

Use /start to open the interactive menu.
Most admin commands work by replying to a user.
"""
    await update.message.reply_html(help_text, reply_markup=back_button("start"))


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "start":
        await query.edit_message_text(
            WELCOME_TEXT,
            reply_markup=main_menu(),
            parse_mode="HTML"
        )
    elif data.startswith("modules:"):
        page = int(data.split(":")[1])
        await query.edit_message_text(
            "<b>All modules:</b>\n_Browse every available module._",
            reply_markup=modules_keyboard(page),
            parse_mode="HTML"
        )
    elif data.startswith("mod:"):
        mod_name = data.split(":", 1)[1]
        await show_module_help(query, mod_name)
    elif data.startswith("cat:"):
        cat = data.split(":", 1)[1]
        await show_module_help(query, cat)
    elif data == "help":
        await help_command(update, context)
    elif data == "noop":
        pass
    elif data == "cancel":
        await query.edit_message_text("❌ Cancelled.")


async def show_module_help(query, mod_name: str):
    helps = {
        "Admin": "🛡 <b>Admin Module</b>\n\n/ban /unban /kick /mute /unmute /promote /demote /settitle /admins",
        "Anime": "🎌 <b>Anime Module</b>\n\n/anime /waifu /neko /quote – Anime related fun commands",
        "Anti-Channel": "🚫 <b>Anti-Channel</b>\n\nAutomatically delete messages from channels. /antichannel on/off",
        "Anti-Spam": "🛡 <b>Anti-Spam</b>\n\nProtects against spam, links, forwards. Configurable.",
        "Antiflood": "🌊 <b>Antiflood</b>\n\n/antiflood on/off | set limit. Auto mute/kick flooders.",
        "Approval": "✅ <b>Approval</b>\n\n/approve /unapprove /approved – Whitelist users from filters & locks.",
        "Bans": "🔨 <b>Bans</b>\n\n/ban /dban /tban /unban – Full ban management with time support.",
        "Birthday": "🎂 <b>Birthday</b>\n\n/setbday /bday – Birthday reminders in groups.",
        "Blocklists": "🚫 <b>Blocklists</b>\n\n/blocklist /addblocklist /rmblocklist – Forbidden words/phrases.",
        "Broadcast": "📢 <b>Broadcast</b>\n\nOwner only. Broadcast message to all groups/users.",
        "Chatbot": "🤖 <b>Chatbot (Groq AI)</b>\n\nMention me or reply to chat with Makima AI. /ai on/off",
        "Connections": "🔗 <b>Connections</b>\n\nConnect groups for remote management.",
        "Disabling": "❌ <b>Disabling</b>\n\n/disable /enable /disabled – Disable commands per chat.",
        "Extras": "✨ <b>Extras</b>\n\nMiscellaneous useful commands.",
        "Federations": "🕸 <b>Federations</b>\n\nMulti-group ban sharing system.",
        "Filters": "🔍 <b>Filters</b>\n\n/filter /stop /filters – Auto reply to keywords.",
        "Formatting": "📝 <b>Formatting</b>\n\nMarkdown/HTML helpers and paste tools.",
        "Fun": "🎉 <b>Fun</b>\n\n/runs /slap /hug /pat and more fun commands.",
        "Greetings": "👋 <b>Greetings</b>\n\n/setwelcome /setgoodbye /welcome on/off",
        "Images": "🖼 <b>Images</b>\n\nImage search, wallpaper, generate (if configured).",
        "Import/Export": "📦 <b>Import/Export</b>\n\nBackup and restore chat settings.",
        "Info": "ℹ️ <b>Info</b>\n\n/info /id /chatinfo – User and chat information.",
        "Karma": "⭐ <b>Karma</b>\n\nUpvote/downvote users with +1 / -1. /karma",
        "Locks": "🔒 <b>Locks</b>\n\n/lock /unlock /locks – Lock media, links, stickers, etc.",
        "Logging": "📋 <b>Logging</b>\n\nSend admin actions to a log channel.",
        "Memes": "😂 <b>Memes</b>\n\nRandom memes and meme generators.",
        "Misc": "🧰 <b>Misc</b>\n\nVarious utility commands.",
        "Night-Mode": "🌙 <b>Night-Mode</b>\n\nAuto lock chat during night hours.",
        "Notes": "📝 <b>Notes</b>\n\n/save /get /notes /clear – Saved notes per chat.",
        "NSFW": "🔞 <b>NSFW</b>\n\nNSFW content filter and controls.",
        "Pin": "📌 <b>Pin</b>\n\n/pin /unpin /pinned – Message pinning.",
        "Purges": "🧹 <b>Purges</b>\n\n/purge /spurge /del – Delete messages in bulk.",
        "Rankings": "🏆 <b>Rankings</b>\n\nMessage count and activity leaderboards.",
        "Reports": "🚨 <b>Reports</b>\n\n/report – Report users to admins.",
        "Rules": "📜 <b>Rules</b>\n\n/setrules /rules /clearrules",
        "SFW": "✅ <b>SFW</b>\n\nSafe-for-work content tools.",
        "Stats": "📊 <b>Stats</b>\n\nBot and chat statistics.",
        "Stickers": "🎨 <b>Stickers</b>\n\nSticker info, pack tools, karma stickers.",
        "Topics": "💬 <b>Topics</b>\n\nForum topic management helpers.",
        "Upload": "⬆️ <b>Upload</b>\n\nFile upload helpers and paste.",
        "Warnings": "⚠️ <b>Warnings</b>\n\n/warn /unwarn /warns /warnlimit /resetwarns",
    }
    text = helps.get(mod_name, f"<b>{mod_name}</b>\n\nModule documentation coming soon.")
    await query.edit_message_text(
        text,
        reply_markup=category_keyboard(mod_name),
        parse_mode="HTML"
    )
