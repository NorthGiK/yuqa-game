from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from src.handlers.telegram.constants import Navigation


main = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Профиль", callback_data=Navigation.profile.value),
        InlineKeyboardButton(text="Инвентарь", callback_data=Navigation.inventory.value),
    ],
    [
        InlineKeyboardButton(text="Бой", callback_data=Navigation.battle.value),
        InlineKeyboardButton(text="Магазин", callback_data=Navigation.shop.value),
    ],
    [
        InlineKeyboardButton(text="Экскурсия по YUQA", callback_data=Navigation.tour.value)
    ]
])