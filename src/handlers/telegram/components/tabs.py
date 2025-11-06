from typing import Iterable
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from src.handlers.telegram import constants
from src.handlers.telegram.constants import Navigation
from src.cards.models import CardInInventory, Rarity as card_rarity


_return_to_main_button = [
    InlineKeyboardButton(
        text="Назад",
        callback_data=constants.Navigation.main)]

main = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Профиль", callback_data=Navigation.profile),
        InlineKeyboardButton(text="Инвентарь", callback_data=Navigation.inventory),
    ],
    [
        InlineKeyboardButton(text="Бой", callback_data=Navigation.battle),
        InlineKeyboardButton(text="Магазин", callback_data=Navigation.shop),
    ],
    [
        InlineKeyboardButton(text="  Экскурсия по YUQA", callback_data=Navigation.tour)
    ]
])

profile = InlineKeyboardMarkup(
    inline_keyboard=[_return_to_main_button],
)

inventory = InlineKeyboardMarkup(inline_keyboard=[
    *([InlineKeyboardButton(text=r.value, callback_data=r.name)] for r in card_rarity),
    _return_to_main_button,
])

def in_inventory_create(cards: Iterable[CardInInventory]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
            *(
                [InlineKeyboardButton(
                    text=card.name,
                    callback_data=str(card.id)
                )] for card in cards
            ),
            [
                InlineKeyboardButton(
                    text="BACK", 
                    callback_data=constants.Navigation.inventory,
                ),
            ],
        ])

battle = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Стандарт", callback_data=Navigation.in_battle.standard),
        InlineKeyboardButton(text="Дуо", callback_data=Navigation.in_battle.duo),
    ],
    [
        InlineKeyboardButton(text="Назад", callback_data=Navigation.main)
    ],
])