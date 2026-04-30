from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def card_review_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Approve", callback_data="approve"),
            InlineKeyboardButton(text="Discard", callback_data="discard"),
        ]
    ])


def deck_picker_keyboard(decks: list[str]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=deck, callback_data=f"deck:{deck}")]
        for deck in decks
    ])
