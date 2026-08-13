# Makima Bot

Anime-themed Telegram group management bot with AI chatbot (Groq), notes, filters, warns, locks, and more.

## Required environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `BOT_TOKEN` | Yes | From @BotFather |
| `MONGO_URI` | Yes | MongoDB Atlas connection string |
| `GROQ_API_KEY` | Yes | From https://console.groq.com |
| `OWNER_ID` | Yes | Your Telegram user ID |
| `API_ID` | No | my.telegram.org (enables Telethon) |
| `API_HASH` | No | my.telegram.org |
| `MONGO_DB` | No | Default: `makima_bot` |
| `GROQ_MODEL` | No | Default: `llama-3.3-70b-versatile` |
| `LOG_LEVEL` | No | Default: `INFO` |
| `PORT` | No | Health check port (default `8080`) |

Use **MongoDB Atlas** (free tier works). Local MongoDB is not available on most PaaS.

---

## Deploy on Koyeb

1. Push this repo to GitHub.
2. Koyeb → **Create App** → **GitHub** → select the repo.
3. **Builder**: Dockerfile (auto-detected).
4. **Instance type**: Free / Nano.
5. **Service type**: Web Service (needed for health checks).
6. **Port**: `8080` (or leave default – app reads `$PORT`).
7. **Health check**: HTTP, path `/`, port `8080`.
8. Add environment variables (see table above).
9. Deploy.

The bot starts polling Telegram and serves `GET /` → `ok` on `$PORT` so health checks pass.

### Koyeb CLI (optional)
```bash
koyeb app init makima-bot --docker
koyeb service create bot --app makima-bot --docker-image ... 
```

---

## Deploy on Render

### Option A – Blueprint (recommended)
1. Push repo to GitHub.
2. Render → **New** → **Blueprint**.
3. Select the repo (uses `render.yaml`).
4. Fill in the secret env vars when prompted.
5. Deploy (runs as a **Background Worker**).

### Option B – Manual Worker
1. **New** → **Background Worker**.
2. Connect repo.
3. Build: `pip install -r requirements.txt`
4. Start: `python main.py`
5. Add env vars from the table.
6. Deploy.

### Option C – Web Service (if you want HTTP health)
Same as worker, but type **Web Service**, start command `python main.py`.  
Health check path: `/`

---

## Deploy with Docker (any VPS)

```bash
cp .env.example .env
# edit .env

docker build -t makima-bot .
docker run -d --env-file .env -p 8080:8080 --name makima makima-bot
```

---

## Local run

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# edit .env
python main.py
```

---

## Project structure

```
├── main.py
├── config.py
├── requirements.txt
├── Dockerfile
├── Procfile
├── render.yaml
├── koyeb.yaml
├── database/
│   └── mongodb.py
└── handlers/
    ├── start.py
    ├── chatbot.py
    ├── helpers.py
    ├── keyboards.py
    ├── telethon_client.py
    ├── health.py
    └── modules/
    ├── start.py
    ├── chatbot.py
    ├── modules/          # feature modules
    └── utils/
        ├── helpers.py
        ├── keyboards.py
        ├── telethon_client.py
        └── health.py
```

## Notes

- Disable **privacy mode** in @BotFather if the bot must see all group messages (filters / antiflood).
- Telethon starts with bot token when `API_ID` + `API_HASH` are set (no phone login).
- First deploy may take 1–2 minutes while indexes are created on MongoDB.
