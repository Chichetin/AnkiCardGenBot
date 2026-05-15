# AnkiCardGen Telegram Bot

A Telegram bot that turns words and phrases into Anki cards. You message a word, GigaChat generates a translation with an example sentence, and the card is added directly to your local Anki collection via AnkiConnect.

## How it works

1. You send a word or phrase to the bot in Telegram.
2. The bot asks GigaChat for a Russian translation and an example sentence in both the source language and Russian.
3. The bot shows a card preview with **Approve** / **Edit** / **Discard** buttons.
4. Optionally tap **Edit** to tweak the generated text before saving (see below).
5. On approve, the bot fetches the list of decks from your running Anki instance and shows a deck picker.
6. After you pick a deck, the bot adds the note to Anki using AnkiConnect.

While a card is waiting for review or deck choice, any extra words you send are pushed onto an in-memory queue. As soon as the current card is resolved (approved, discarded, or fails), the queue is drained automatically.

### Card format

- **Front** — the word/phrase you sent.
- **Back** — GigaChat output, formatted as:
  ```
  Translation: <Russian translation>
  Example EN: <example in original language>
  Example RU: <example in Russian>
  ```

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) for dependency management
- [Anki](https://apps.ankiweb.net/) running locally
- [AnkiConnect](https://ankiweb.net/shared/info/2055492159) add-on installed in Anki
- A Telegram bot token (from [@BotFather](https://t.me/BotFather))
- GigaChat API credentials ([developers.sber.ru/portal/products/gigachat-api](https://developers.sber.ru/portal/products/gigachat-api))

## Setup

1. Clone the repo and install dependencies:
   ```bash
   git clone <repo-url>
   cd AnkiCardGen_Bot
   uv sync
   ```

2. Create a `.env` file from the template:
   ```bash
   cp .env.example .env
   ```

3. Fill in the values:
   ```env
   TELEGRAM_TOKEN=your_telegram_bot_token
   GIGACHAT_CREDENTIALS=your_gigachat_credentials
   ANKI_URL=http://localhost:8765
   ANKI_MODEL=Basic
   ```

   `ANKI_MODEL` must match an existing note type in your Anki collection. The note type must have fields named **Front** and **Back** (the default `Basic` type already does).

4. Make sure Anki is open and AnkiConnect is listening on `ANKI_URL` (default `http://localhost:8765`).

5. Start the bot:
   ```bash
   uv run python main.py
   ```

## Usage

In Telegram:

- Send any word or phrase as a plain message — the bot replies with a generated card preview.
- Tap **Approve** to pick a deck and save, **Edit** to revise the card text, or **Discard** to drop the card.
- When editing, the bot echoes the current card as plain text — reply with the corrected version where the **first line is the front** and **the rest is the back**. The preview is then shown again with the same buttons.
- Send more words while reviewing — they go into a queue and will be processed one by one after the current card is resolved. (While editing, your next message is treated as the edited card, not queued.)

If Anki is not reachable when you approve a card, the bot tells you so and moves on to the next queued word.

## Project layout

```
main.py                  Bot entry point — wires services and starts polling
config.py                Environment-driven settings (pydantic-settings)
models.py                CardData dataclass
bot/
  handlers/card_flow.py  Aiogram router: message handling, FSM, callbacks
  keyboards.py           Inline keyboards (review buttons, deck picker)
  states.py              FSM states: reviewing, editing, choosing_deck
services/
  gigachat.py            GigaChat client wrapper, prompt template
  anki.py                AnkiConnect HTTP client (deckNames, addNote)
  word_queue.py          In-memory FIFO queue for incoming words
tests/                   Pytest suite for the service layer
```

The bot is single-process and stateless across restarts — the queue and FSM state live in memory only.

## Development

Run tests:
```bash
uv run pytest
```

The test suite covers the AnkiConnect client (mocked HTTP), the GigaChat service (mocked client), and the word queue.

## Troubleshooting

- **"Could not reach Anki. Is it running?"** — Anki is closed, AnkiConnect isn't installed, or `ANKI_URL` is wrong. Open Anki and verify the add-on is loaded.
- **"Failed to generate card"** — GigaChat call failed. Check `GIGACHAT_CREDENTIALS` and network access.
- **`addNote` errors about unknown fields** — Your `ANKI_MODEL` note type doesn't have `Front`/`Back` fields. Either set `ANKI_MODEL` to a type that does (e.g. `Basic`) or adjust the field mapping in `services/anki.py`.
- **Card not added even though no error appeared** — AnkiConnect rejects duplicates by default (`allowDuplicate: false`). Check the deck for an existing identical front.
