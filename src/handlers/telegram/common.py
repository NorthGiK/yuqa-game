from typing import Optional, Union

from aiogram import F, Router
from aiogram.filters import (
    # Command,
    CommandStart,
)
from aiogram.types import (
    Message,
    CallbackQuery,
    # KeyboardButton,
    # ReplyKeyboardMarkup,
    # InlineKeyboardButton,
    # InlineKeyboardMarkup,
)

from src.handlers.telegram import constants
from src.handlers.telegram.components import tabs
from src.users.crud import check_user, create_user, get_user


router = Router()

async def _start(msg: Union[Message, CallbackQuery]):
    user = msg.from_user
    if user is None:
        await msg.reply(f"чето не так с юзером, стань нормальным") #type:ignore
        return

    username: Optional[str] = user.username
    user_id: int = user.id

    if not await check_user(user_id):
        await create_user(user_id)
        await msg.answer(f"Добро пожаловать, пидр по имени {username}! {user_id}",
                        reply_markup=tabs.main)
        return

    answer = dict(
        text=f"Привет, пидр по имени {username}",
        reply_markup=tabs.main,
    )
    if isinstance(msg, CallbackQuery):
        await msg.answer() #type:ignore
        await msg.message.answer(**answer)#type:ignore
    else:
        await msg.answer(**answer) #type:ignore

@router.message(CommandStart())
async def start_handler(msg: Message):
    await _start(msg)

@router.callback_query(F.data == constants.Navigation.main)
async def main_handler(clbk: CallbackQuery):
    await _start(clbk)


@router.callback_query(F.data == constants.Navigation.inventory)
async def profile_handler(clbk: CallbackQuery):
    await clbk.answer()
    await clbk.message.answer( #type:ignore
        f"Инвентарь {clbk.from_user.username}\n"
        ,
        reply_markup=tabs.inventory,
    )


@router.callback_query(F.data == constants.Navigation.profile)
async def inventory_handler(clbk: CallbackQuery):
    await clbk.answer()

    id = clbk.from_user.id
    user = await get_user(id)
    if user is None:
        await clbk.answer("type `/start` first")
        return

    if clbk.message is None:
        return

    await clbk.message.answer(
        f"роль: {user.role}\n"
        f"рейтинг: {user.rating}\n"
        f"всего карт: {user.cards}\n"
        ,
        reply_markup=tabs.profile,
    )


@router.callback_query(F.data == constants.Navigation.battle)
async def battle_handler(clbk: CallbackQuery):
    await clbk.answer()

    if clbk.message is None:
        return

    await clbk.message.answer(text="Выбирай тип боя",
                              reply_markup=tabs.battle)