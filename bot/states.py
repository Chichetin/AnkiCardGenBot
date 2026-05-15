from aiogram.fsm.state import State, StatesGroup


class CardFlow(StatesGroup):
    reviewing = State()
    editing = State()
    choosing_deck = State()
