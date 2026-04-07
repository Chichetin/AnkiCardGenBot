# AnkiCardGen Telegram Bot

Telegram bot that turns words into Anki cards:

1. You send a word/phrase to the bot.
2. Qwen generates Russian translation + short learning description.
3. Bot sends card preview in Telegram.
4. You approve it and choose target deck.
5. Bot adds note directly to your local Anki via AnkiConnect.

## Requirements

- Python 3.10+
- Anki Desktop installed and running
- AnkiConnect plugin installed in Anki (`2055492159`)
- Telegram bot token from BotFather
- Qwen-compatible API key

## Setup

```bash
cd /home/chichetin/AnkiCardGen_Bot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Then fill `.env` values.

## Run

```bash
cd /home/chichetin/AnkiCardGen_Bot
source .venv/bin/activate
python main.py
```

## Commands

- `/start` - intro
- `/help` - usage
- `/decks` - list available Anki decks

## Notes

- This project keeps pending cards only in memory (no database).
- Anki must stay open while using the bot, because syncing goes through AnkiConnect (`http://127.0.0.1:8765` by default).
- Cards are saved as `Basic` note type:
  - Front: word + Russian translation
  - Back: AI description

