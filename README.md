# Makima – Telegram Group Management Bot

Anime-themed group & channel management bot with **Groq AI Chatbot** and **MongoDB**.

Inspired by the Makima character (Chainsaw Man). Elegant, powerful, modular.

## Features (matching the screenshots)

### Page 1 Modules
- Admin, Anime, Anti-Channel
- Anti-Spam, Antiflood, Approval
- Bans, Birthday, Blocklists
- Broadcast, Chatbot (Groq AI), Connections
- Disabling, Extras, Federations
- Filters, Formatting, Fun
- Greetings, Images, Import/Export
- Info, Karma, Locks

### Page 2 Modules
- Logging, Memes, Misc
- Night-Mode, Notes, NSFW
- Pin, Purges, Rankings
- Reports, Rules, SFW
- Stats, Stickers, Topics
- Upload, Warnings

## Tech Stack
- Python 3.10+
- python-telegram-bot 21.x
- Groq API (llama-3.3-70b-versatile or any model)
- MongoDB (Motor async driver)
- Fully modular – each feature in its own file

## Quick Start

1. **Clone / Unzip**
   ```bash
   cd makima_bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure**
   ```bash
   cp .env.example .env
   nano .env
   ```
   Fill in:
   - `BOT_TOKEN` → from @BotFather
   - `GROQ_API_KEY` → from https://console.groq.com
   - `MONGO_URI` → local or MongoDB Atlas
   - `OWNER_ID` → your Telegram user ID (@userinfobot)

4. **Run**
   ```bash
   python main.py
   ```

## AI Chatbot Usage
- In **private chat**: just talk to the bot
- In **groups**: mention the bot (`@YourBot`) or reply to its messages
- Admins can control with `/ai` settings (extendable)

## Project Structure
```
makima_bot/
├── main.py                 # Entry point
├── config.py
├── requirements.txt
├── .env.example
├── database/
│   └── mongodb.py
├── handlers/
│   ├── start.py            # /start + menus
│   ├── chatbot.py          # Groq AI
│   └── modules/            # All feature modules
│       ├── admin.py
│       ├── warnings.py
│       ├── locks.py
│       ├── filters.py
│       ├── notes.py
│       ├── greetings.py
│       ├── antiflood.py
│       ├── ... (one file per module)
├── utils/
│   ├── helpers.py
│   └── keyboards.py
└── README.md
```

## Adding New Modules
1. Create `handlers/modules/yourmodule.py`
2. Implement `get_handlers()` that returns a list of handlers
3. Import & add to `handlers/modules/__init__.py`

## Notes
- Some advanced modules (Federations, full Broadcast, Night-Mode scheduler, NSFW detection, etc.) have basic structure and can be extended.
- For production: use a process manager (systemd / pm2 / docker) and MongoDB Atlas.
- Rate limits: Groq free tier has limits – upgrade if needed.

Made with ❤️ for elegant group control.

## Deployment (Docker / Railway / Render / VPS)

### Required Environment Variables
```
BOT_TOKEN=
API_ID=
API_HASH=
GROQ_API_KEY=
MONGO_URI=mongodb+srv://...
MONGO_DB=makima_bot
OWNER_ID=
GROQ_MODEL=llama-3.3-70b-versatile
```

### Docker (local or any VPS)
```bash
docker build -t makima-bot .
docker run -d --env-file .env --name makima makima-bot
```

### Railway / Render / Koyeb
1. Connect your GitHub repo
2. Set the environment variables above
3. The included `Dockerfile` will be detected automatically
4. Deploy

If the platform asks for a start command, use:
```
python main.py
```

### Important
- Use **MongoDB Atlas** (free tier works) – local MongoDB is not available on most PaaS.
- Make sure the bot has privacy mode disabled in @BotFather if you want it to read all group messages for filters/antiflood.
