from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.keyboards import card_review_keyboard, deck_picker_keyboard
from bot.states import CardFlow
from models import CardData
from services.anki import AnkiService, AnkiError
from services.gigachat import GigaChatService, GigaChatError
from services.word_queue import WordQueue

router = Router()


async def _start_card_flow(
    message: Message,
    state: FSMContext,
    gigachat: GigaChatService,
    word: str,
) -> None:
    await message.answer(f"Generating card for: {word}...")

    try:
        card = await gigachat.generate_card(word)
    except GigaChatError:
        await message.answer(f'Failed to generate card for "{word}". Skipping.')
        return

    await state.update_data(card=card)
    await state.set_state(CardFlow.reviewing)
    await message.answer(
        f"*{card.front}*\n\n{card.back}",
        parse_mode="Markdown",
        reply_markup=card_review_keyboard(),
    )


async def _process_next_in_queue(
    message: Message,
    state: FSMContext,
    gigachat: GigaChatService,
    queue: WordQueue,
) -> None:
    next_word = queue.pop()
    while next_word is not None:
        await _start_card_flow(message, state, gigachat, next_word)
        if await state.get_state() == CardFlow.reviewing:
            return
        next_word = queue.pop()


@router.message(CardFlow.reviewing)
@router.message(CardFlow.choosing_deck)
async def queue_during_flow(message: Message, queue: WordQueue):
    queue.push(message.text.strip())
    await message.answer(f"Added to queue ({queue.size()} pending).")


@router.message()
async def handle_word(
    message: Message,
    state: FSMContext,
    gigachat: GigaChatService,
    queue: WordQueue,
):
    await _start_card_flow(message, state, gigachat, message.text.strip())
    if await state.get_state() != CardFlow.reviewing:
        await _process_next_in_queue(message, state, gigachat, queue)


@router.callback_query(CardFlow.reviewing, F.data == "discard")
async def handle_discard(
    callback: CallbackQuery,
    state: FSMContext,
    gigachat: GigaChatService,
    queue: WordQueue,
):
    await state.clear()
    await callback.message.edit_text("Card discarded.")
    await callback.answer()
    await _process_next_in_queue(callback.message, state, gigachat, queue)


@router.callback_query(CardFlow.reviewing, F.data == "approve")
async def handle_approve(
    callback: CallbackQuery,
    state: FSMContext,
    anki: AnkiService,
    gigachat: GigaChatService,
    queue: WordQueue,
):
    try:
        decks = await anki.get_decks()
    except AnkiError:
        await state.clear()
        await callback.message.edit_text("Could not reach Anki. Is it running?")
        await callback.answer()
        await _process_next_in_queue(callback.message, state, gigachat, queue)
        return

    await state.set_state(CardFlow.choosing_deck)
    await callback.message.edit_text("Choose a deck:", reply_markup=deck_picker_keyboard(decks))
    await callback.answer()


@router.callback_query(CardFlow.choosing_deck, F.data.startswith("deck:"))
async def handle_deck_choice(
    callback: CallbackQuery,
    state: FSMContext,
    anki: AnkiService,
    gigachat: GigaChatService,
    queue: WordQueue,
):
    deck = callback.data.removeprefix("deck:")
    data = await state.get_data()
    card: CardData = data["card"]

    try:
        await anki.add_note(deck, card.front, card.back)
    except AnkiError as e:
        await state.clear()
        await callback.message.edit_text(f"Failed to add card: {e}")
        await callback.answer()
        await _process_next_in_queue(callback.message, state, gigachat, queue)
        return

    await state.clear()
    await callback.message.edit_text(f'Card added to "{deck}".')
    await callback.answer()
    await _process_next_in_queue(callback.message, state, gigachat, queue)
