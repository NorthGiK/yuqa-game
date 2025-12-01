from typing import Annotated, Iterable

from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from src.handlers.telegram.constants import Navigation
from src.cards.models import MCard, Rarity
from src.handlers.rabbit.constants import PIT_GOLD


def _return_to(where: Annotated[str, Navigation], inline: bool = True) -> list[InlineKeyboardButton] | list[KeyboardButton]:
    if inline:
        return [InlineKeyboardButton(
            text="Назад",
            callback_data=where, #type:ignore
        )]
    return [
        KeyboardButton(text="Назад ↵")
    ]

main = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Профиль", callback_data=Navigation.profile),
        InlineKeyboardButton(text="Инвентарь", callback_data=Navigation.inventory),
    ],
    [
        InlineKeyboardButton(text="Бой", callback_data=Navigation.battle),
        InlineKeyboardButton(text="Магазин", callback_data=Navigation.shop),
    ],
    [ InlineKeyboardButton(text="Баннеры", callback_data=Navigation.gacha) ],
    [
        InlineKeyboardButton(text="  Экскурсия по YUQA", callback_data=Navigation.tour)
    ]
])

profile = InlineKeyboardMarkup(
    inline_keyboard=[_return_to(Navigation.main)],
)

inventory = InlineKeyboardMarkup(inline_keyboard=[
    *(
        [InlineKeyboardButton(
            text=r.value,
            callback_data=r.name,
        )] for r in Rarity
    ),
    _return_to(Navigation.main),
])

def create_card_in_inventory_callback(id: int) -> str:
    return f"show_card_in_inventory:{id}"

def in_inventory_create(cards: Iterable[MCard]) -> InlineKeyboardMarkup:
    cards_buttons = [[InlineKeyboardButton(
                    text=f"{card.atk} {card.hp} {card.def_}\n\t{card.name}",
                    callback_data=create_card_in_inventory_callback(card.id),
                )] for card in cards]

    return InlineKeyboardMarkup(inline_keyboard=[
            *cards_buttons,
            _return_to(Navigation.inventory),
        ])

battle = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(text="Стандарт"), #, callback_data=Navigation.in_battle.standard),
        KeyboardButton(text="Дуо"), #, callback_data=Navigation.in_battle.duo),
    ],
    _return_to("", False),
], resize_keyboard=True)

gacha = InlineKeyboardMarkup(inline_keyboard=[
    [ InlineKeyboardButton(text="Золотая крутка", callback_data=PIT_GOLD) ],
    _return_to(Navigation.main),
])