from __future__ import annotations

import logging
from dataclasses import dataclass, field

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from anki_handler import AnkiConnectClient, AnkiConnectError
from card_generator import CardData, QwenCardGenerator
from config import Settings, load_settings


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


@dataclass
class UserSession:
    pending_card: CardData | None = None
    awaiting_deck_choice: bool = False
    deck_options: list[str] = field(default_factory=list)


SESSIONS: dict[int, UserSession] = {}


APPROVAL_KEYBOARD = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton("Approve", callback_data="approve"),
            InlineKeyboardButton("Reject", callback_data="reject"),
        ]
    ]
)


BOT_SETTINGS: Settings | None = None
CARD_GENERATOR: QwenCardGenerator | None = None
ANKI_CLIENT: AnkiConnectClient | None = None



def get_session(user_id: int) -> UserSession:
    if user_id not in SESSIONS:
        SESSIONS[user_id] = UserSession()
    return SESSIONS[user_id]



def require_services() -> tuple[QwenCardGenerator, AnkiConnectClient]:
    if CARD_GENERATOR is None or ANKI_CLIENT is None:
        raise RuntimeError("Services are not initialized.")
    return CARD_GENERATOR, ANKI_CLIENT


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    del context
    if not update.message or not update.effective_user:
        return

    await update.message.reply_text(
        "Send me an English word or phrase.\n"
        "I will generate an Anki card preview (translation + description), then you approve it."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    del context
    if not update.message:
        return

    await update.message.reply_text(
        "How to use:\n"
        "1) Send a word or phrase\n"
        "2) Tap Approve/Reject\n"
        "3) If approved, send deck number to add the card\n\n"
        "Commands:\n"
        "/start - start bot\n"
        "/help - show this help\n"
        "/decks - list available Anki decks"
    )


async def decks_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    del context
    if not update.message:
        return

    _, anki = require_services()
    try:
        deck_names = await anki.deck_names()
    except AnkiConnectError as exc:
        await update.message.reply_text(f"Anki error: {exc}")
        return

    if not deck_names:
        await update.message.reply_text("No decks found in Anki.")
        return

    listing = "\n".join(f"{idx + 1}. {name}" for idx, name in enumerate(deck_names))
    await update.message.reply_text(f"Available decks:\n{listing}")


async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    del context
    if not update.message or not update.effective_user:
        return

    text = update.message.text.strip()
    if not text:
        await update.message.reply_text("Please send a non-empty word or phrase.")
        return

    session = get_session(update.effective_user.id)

    if session.awaiting_deck_choice and session.pending_card is not None:
        await handle_deck_choice(update, session, text)
        return

    generator, _ = require_services()
    await update.message.reply_text("Generating card with Qwen...")

    try:
        card = await generator.generate_card(text)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Failed to generate card")
        await update.message.reply_text(f"Generation failed: {exc}")
        return

    session.pending_card = card
    session.awaiting_deck_choice = False
    session.deck_options = []

    await update.message.reply_text(format_card_preview(card), reply_markup=APPROVAL_KEYBOARD)


async def on_approval_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    del context
    if not update.callback_query or not update.effective_user:
        return

    query = update.callback_query
    session = get_session(update.effective_user.id)

    await query.answer()

    if session.pending_card is None:
        await query.edit_message_text("No pending card. Send a new word.")
        return

    if query.data == "reject":
        session.pending_card = None
        session.awaiting_deck_choice = False
        session.deck_options = []
        await query.edit_message_text("Card rejected. Send another word.")
        return

    _, anki = require_services()
    try:
        decks = await anki.deck_names()
    except AnkiConnectError as exc:
        await query.edit_message_text(f"Anki error: {exc}")
        return

    if not decks:
        await query.edit_message_text("No Anki decks found. Create a deck in Anki first.")
        return

    session.awaiting_deck_choice = True
    session.deck_options = decks

    deck_list = "\n".join(f"{idx + 1}. {name}" for idx, name in enumerate(decks))
    await query.edit_message_text(
        "Approved. Reply with the deck number to save this card:\n"
        f"{deck_list}"
    )


async def handle_deck_choice(update: Update, session: UserSession, choice_text: str) -> None:
    if not update.message:
        return

    if not choice_text.isdigit():
        await update.message.reply_text("Please send a deck number (for example: 1).")
        return

    index = int(choice_text) - 1
    if index < 0 or index >= len(session.deck_options):
        await update.message.reply_text("Deck number is out of range. Try again.")
        return

    card = session.pending_card
    if card is None:
        await update.message.reply_text("No pending card. Send a new word.")
        session.awaiting_deck_choice = False
        session.deck_options = []
        return

    deck_name = session.deck_options[index]
    front = f"{card.word}\n{card.translation_ru}"
    back = card.description

    _, anki = require_services()
    try:
        note_id = await anki.add_basic_note(deck_name=deck_name, front=front, back=back)
        await anki.sync()
    except AnkiConnectError as exc:
        await update.message.reply_text(f"Failed to add note: {exc}")
        return

    await update.message.reply_text(
        f"Added to deck '{deck_name}'. Note ID: {note_id}\nSend another word."
    )
    session.pending_card = None
    session.awaiting_deck_choice = False
    session.deck_options = []



def format_card_preview(card: CardData) -> str:
    return (
        "Card preview:\n\n"
        f"Word: {card.word}\n"
        f"Russian: {card.translation_ru}\n\n"
        f"Description:\n{card.description}"
    )



def build_application(settings: Settings) -> Application:
    application = Application.builder().token(settings.telegram_bot_token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("decks", decks_command))
    application.add_handler(CallbackQueryHandler(on_approval_callback, pattern="^(approve|reject)$"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))

    return application



def main() -> None:
    global BOT_SETTINGS, CARD_GENERATOR, ANKI_CLIENT

    BOT_SETTINGS = load_settings()
    CARD_GENERATOR = QwenCardGenerator(
        api_key=BOT_SETTINGS.qwen_api_key,
        model=BOT_SETTINGS.qwen_model,
        base_url=BOT_SETTINGS.qwen_base_url,
    )
    ANKI_CLIENT = AnkiConnectClient(url=BOT_SETTINGS.anki_connect_url)

    app = build_application(BOT_SETTINGS)
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

