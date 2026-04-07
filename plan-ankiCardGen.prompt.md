# Plan: Telegram Bot for Anki Card Generation

Create a Python-based Telegram bot that generates Anki cards with Russian translations and AI-powered descriptions. Users send words, review generated cards in Telegram, approve/reject them, and approved cards are automatically added to their Anki collection.

## Steps

1. **Set up project structure and dependencies**
   - Create `requirements.txt` with: `python-telegram-bot`, `openai`, `python-dotenv`
   - Initialize main files: `main.py` (bot entry point), `config.py`, `.env` (for secrets)

2. **Implement core bot handler**
   - Create message handler in `main.py` to receive words from users
   - Set up Telegram bot token authentication via environment variable
   - Route incoming messages to card generation workflow

3. **Build translation & AI description module** (`card_generator.py`)
   - Implement translation function (word -> Russian using Qwen API)
   - Implement AI description generator using Qwen API to create learning descriptions
   - Return formatted card data (word, translation, description)

4. **Create card preview & approval flow**
   - Send generated card to user as formatted text with inline keyboard buttons (Approve/Reject)
   - Store pending cards only in temporary in-memory user session state
   - Handle button callbacks to track user decisions

5. **Integrate direct Anki sync** (`anki_handler.py`)
   - Use AnkiConnect API to communicate with local Anki Desktop
   - On approval, let user pick target deck from existing decks
   - Add card directly as `Basic` note (Front: word + translation, Back: description)

6. **Deploy and configure**
   - Set up environment variables (Telegram token, Qwen API key)
   - Ensure Anki Desktop is running with AnkiConnect plugin installed
   - Test end-to-end workflow locally before deployment


