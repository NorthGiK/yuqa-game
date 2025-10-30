import asyncio
from typing import Optional

from aiogram import F, Router
from aiogram.filters import (
    Command,
    CommandStart,
)
from aiogram.types import (
    Message,
    CallbackQuery,
    KeyboardButton,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from src.handlers.telegram.components import tabs
from src.users.crud import check_user, create_user


router = Router()

@router.message(CommandStart())
async def start_handler(msg: Message):
    user = msg.from_user
    if user is None:
        await msg.reply(f"чето не так с юзером, стань нормальным")
        return

    username: Optional[str] = user.username
    user_id: int = user.id

    if not await check_user(user_id):
        asyncio.create_task(create_user(user_id))
        await msg.reply(f"Добро пожаловать, пидр по имени {username}! {user_id}",
                        reply_markup=tabs.main)
        return

    await msg.reply(f"Привет, пидр по имени {username} {user_id}",
                    reply_markup=tabs.main)

# @