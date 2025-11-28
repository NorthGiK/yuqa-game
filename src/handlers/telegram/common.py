from typing import Optional, Union

from aiogram import F, Router
from aiogram.filters import (
    CommandStart,
    Command,
)
from aiogram.types import (
    Message,
    CallbackQuery,
)

from src.handlers.telegram import constants
from src.handlers.telegram.components import tabs
from src.cards.models import MCard, Rarity
from src.cards.crud import get_cards_by_rarity
from src.logs import dev_configure, get_logger
from src.users.crud import check_user, create_user, get_user
from src.utils.decorators import log_func_call
from src.utils.redis_cache import redis


router = Router()

log = get_logger(__name__)
dev_configure()

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

@router.message(F.text == "Назад ↵")
async def back_to_main_handler(msg: Message) -> None:
    await _start(msg)


@router.callback_query(F.data == constants.Navigation.inventory)
async def profile_handler(clbk: CallbackQuery):
    await clbk.answer("")
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
    cards: list[MCard] = await get_cards_by_rarity(rarity=rarity, user_id=user_id)

    page_num = int(await redis.get(f"inventory:{rarity.name}"))

    if page_num + 10 > len(cards):
        end = len(cards)
    else:
        end = page_num + 10

    cards = cards[page_num:end]

    await clbk.answer("")
    await clbk.message.answer(f"Инвентарь {clbk.from_user.username}",#type:ignore
                              reply_markup=tabs.in_inventory_create(cards)) #type:ignore 


@router.callback_query(F.data == Rarity.legendary.name)
async def legendary_cards_handler(clbk: CallbackQuery) -> None:
    await redis.setex(f"inventory:{Rarity.legendary.name}", 999, 0)
    return await _show_cards_for_rarity(clbk=clbk, rarity=Rarity.legendary)


@router.callback_query(F.data == constants.Navigation.profile)
async def inventory_handler(clbk: CallbackQuery):
    await clbk.answer("")

    id = clbk.from_user.id
    user = await get_user(id)
    if user is None:
        await clbk.answer("type `/start` first")
        return

    if clbk.message is None:
        return
    
    await clbk.message.answer(
        f"рейтинг: {user.rating}\n"
        ,
        reply_markup=tabs.profile,
    )


@router.callback_query(F.data == constants.Navigation.battle)
async def battle_handler(clbk: CallbackQuery):
    await clbk.answer("ok")

    if clbk.message is None:
        return

    await clbk.message.answer(text="Выбирай тип боя",
                              reply_markup=tabs.battle)
