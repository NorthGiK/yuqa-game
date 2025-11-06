from typing import Optional, Union

from aiogram import F, Router
from aiogram.filters import (
    CommandStart,
)
from aiogram.types import (
    Message,
    CallbackQuery,
)

from src.handlers.telegram import constants
from src.handlers.telegram.components import tabs
from src.cards.models import CardInInventory, Rarity
from src.cards.crud import get_card, get_cards_by_rarity
from src.shared.redis_broker import redis
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

async def _show_cards_for_rarity(
    clbk: CallbackQuery,
    rarity: Rarity,
) -> None:
    user_id: int = clbk.from_user.id #type:ignore
    cards: list[CardInInventory] | None = await get_cards_by_rarity(rarity=rarity, user_id=user_id)

    await clbk.answer("")
    await clbk.message.answer(f"Инвентарь {clbk.from_user.username}",
                              reply_markup=tabs.in_inventory_create(cards)) #type:ignore
    

@router.callback_query(F.data == Rarity.legendary.name)
async def legendary_cards_handler(clbk: CallbackQuery) -> None:
    return await _show_cards_for_rarity(clbk=clbk, rarity=Rarity.legendary)


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
        # f"роль: {user.role}\n"
        f"рейтинг: {user.rating}\n"
        # f"всего карт: {user.cards}\n"
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