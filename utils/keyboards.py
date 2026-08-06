from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# All modules exactly as shown in screenshots
MODULES_PAGE_1 = [
    "Admin", "Anime", "Anti-Channel",
    "Anti-Spam", "Antiflood", "Approval",
    "Bans", "Birthday", "Blocklists",
    "Broadcast", "Chatbot", "Connections",
    "Disabling", "Extras", "Federations",
    "Filters", "Formatting", "Fun",
    "Greetings", "Images", "Import/Export",
    "Info", "Karma", "Locks",
]

MODULES_PAGE_2 = [
    "Logging", "Memes", "Misc",
    "Night-Mode", "Notes", "NSFW",
    "Pin", "Purges", "Rankings",
    "Reports", "Rules", "SFW",
    "Stats", "Stickers", "Topics",
    "Upload", "Warnings",
]

def main_menu() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("📚 All Modules", callback_data="modules:1")],
        [
            InlineKeyboardButton("🛡 Admin", callback_data="cat:Admin"),
            InlineKeyboardButton("🎌 Anime", callback_data="cat:Anime"),
        ],
        [
            InlineKeyboardButton("🚫 Anti-Spam", callback_data="cat:Anti-Spam"),
            InlineKeyboardButton("🔒 Locks", callback_data="cat:Locks"),
        ],
        [
            InlineKeyboardButton("🎉 Fun", callback_data="cat:Fun"),
            InlineKeyboardButton("🛠 Tools", callback_data="cat:Tools"),
        ],
        [InlineKeyboardButton("🤖 AI Chatbot", callback_data="cat:Chatbot")],
        [InlineKeyboardButton("📖 Help & Commands", callback_data="help")],
        [
            InlineKeyboardButton("➕ Add Me To Your Group", url="https://t.me/YOUR_BOT_USERNAME?startgroup=true"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)

def modules_keyboard(page: int = 1) -> InlineKeyboardMarkup:
    modules = MODULES_PAGE_1 if page == 1 else MODULES_PAGE_2
    buttons = []
    row = []
    for i, mod in enumerate(modules, 1):
        row.append(InlineKeyboardButton(mod, callback_data=f"mod:{mod}"))
        if i % 3 == 0:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    # Pagination
    nav = []
    if page > 1:
        nav.append(InlineKeyboardButton("◀️", callback_data=f"modules:{page-1}"))
    nav.append(InlineKeyboardButton(f"{page}/2", callback_data="noop"))
    if page < 2:
        nav.append(InlineKeyboardButton("▶️", callback_data=f"modules:{page+1}"))
    buttons.append(nav)
    buttons.append([InlineKeyboardButton("⬅️ Back", callback_data="start")])
    return InlineKeyboardMarkup(buttons)

def category_keyboard(category: str) -> InlineKeyboardMarkup:
    """Simple back button for category views"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Back to Modules", callback_data="modules:1")]
    ])

def back_button(callback: str = "start") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data=callback)]])

def confirm_keyboard(action: str, user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Confirm", callback_data=f"confirm:{action}:{user_id}"),
            InlineKeyboardButton("❌ Cancel", callback_data="cancel"),
        ]
    ])
