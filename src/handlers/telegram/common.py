from typing import Union

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message

from src.cards.crud import CardRepository
from src.cards.models import MCard, Rarity
from src.core.settings import config
from src.handlers.raw_text import (
    ADMIN_PANEL_MESSAGE,
    BATTLE_CHOICE_MESSAGE,
    COMMON_SHOP_MESSAGE,
    DONUT_MESSAGE,
    GREETING_NEW_USER_MESSAGE,
    GREETING_USER_MESSAGE,
    BASE_USERNAME,
    PARSE_PROFILE_INFO,
    SHOP_CHOICE_MESSAGE,
    SPECIAL_SHOP_MESSAGE,
)
from src.handlers.telegram.constants import (
    CURRENT_IVENTORY_PAGE_REDIS,
    Navigation,
)
from src.handlers.telegram.components import tabs
from src.logs import dev_configure, get_logger
from src.users.crud import UserRepository
from src.utils.redis_cache import redis


router = Router()

log = get_logger(__name__)
# TODO: Поменять на обычную конфигурацию для прода
dev_configure()


async def _start(msg: Union[Message, CallbackQuery]):
    """Отправляет приветственное сообщение пользователю при команде `/start`"""
    user = msg.from_user
    if user is None:
        return

    username: str = user.username or BASE_USERNAME
    user_id: int = user.id
    show_markup = tabs.admin_panel if user_id == config.tg_workflow.ADMIN_ID else tabs.main

    # если пользователя нет в бд, то создать его
    if not await UserRepository.check_user(user_id):
        await UserRepository.create_user(user_id)
        await msg.answer(
            GREETING_NEW_USER_MESSAGE.format(username=username),
            reply_markup=show_markup,
        )
        return

    # поприветсовать существующего пользователя
    if isinstance(msg, CallbackQuery):
        await msg.answer()
        await msg.message.answer(
            GREETING_USER_MESSAGE.format(username=username),
            reply_markup=show_markup,
        )
    else:
        await msg.answer(
            GREETING_USER_MESSAGE.format(username=username),
            reply_markup=show_markup,
        )


@router.message(CommandStart())
async def start_handler(msg: Message):
    """отправить приветсвие пользователю по команде `/start`"""
    await _start(msg)


@router.callback_query(F.data == Navigation.main)
async def main_handler(clbk: CallbackQuery):
    """отправить приветсвие пользователю, если он нажал инлайн-кнопку назад"""
    await _start(clbk)


@router.message(F.text == "Назад")
async def back_to_main_handler(msg: Message) -> None:
    """отправить приветсвие пользователю, если он нажал обычную кнопку назад"""
    await _start(msg)


@router.callback_query(F.data == Navigation.profile)
async def profile_handler(clbk: CallbackQuery) -> None:
    """отправить пользователю данные его профиля при нажатии на инлайн-кнопку в главном меню"""
    await clbk.answer()

    profile = await UserRepository.get_profile(clbk.from_user.id)
    await clbk.message.answer(
        PARSE_PROFILE_INFO(profile),
        reply_markup=tabs.profile,
    )


async def _show_cards_for_rarity(
    clbk: CallbackQuery,
    rarity: Rarity,
) -> None:
    user_and_rarity = dict(
        user = clbk.from_user.id,
        rarity = rarity,
    )
    cards: list[MCard] = await CardRepository.get_cards_by_rarity(**user_and_rarity)
    page_num: int = int(await redis.get(CURRENT_IVENTORY_PAGE_REDIS.format(**user_and_rarity)))

    # показать карты от индекса page_num до конца, если меньше 10 карт можно показать.
    # иначе просто от page_num до page_num + 10
    card_to_show = slice(page_num, page_num + 10 if page_num + 10 > len(cards) else len(cards))
    cards = cards[card_to_show]

    await clbk.answer()
    await clbk.message.answer(
        f"Инвентарь {clbk.from_user.username}",
        reply_markup=tabs.in_inventory_create(cards),
    )


@router.callback_query(F.data == Rarity.legendary.name)
async def legendary_cards_handler(clbk: CallbackQuery) -> None:
    inventory_redis_key: str = CURRENT_IVENTORY_PAGE_REDIS.format(
            user_id=clbk.from_user.id,
            rarity=Rarity.legendary.name)

    await redis.setex(inventory_redis_key, 180, 0)
    return await _show_cards_for_rarity(clbk=clbk, rarity=Rarity.legendary)


@router.callback_query(F.data == Navigation.inventory)
async def inventory_handler(clbk: CallbackQuery) -> None:
    await clbk.answer()
    await clbk.message.answer(
        SHOP_CHOICE_MESSAGE,
        reply_markup=tabs.inventory,
    )


@router.callback_query(F.data == Navigation.battle)
async def battle_handler(clbk: CallbackQuery) -> None:
    await clbk.answer()
    await clbk.message.answer(BATTLE_CHOICE_MESSAGE, reply_markup=tabs.battle)


@router.callback_query(F.data == Navigation.admin)
async def show_admin_panel(clbk: CallbackQuery) -> None:
    await clbk.answer()
    await clbk.message.answer(
        ADMIN_PANEL_MESSAGE,
        reply_markup=tabs.admin_panel,
    )


@router.callback_query(F.data == Navigation.shop)
async def show_shop_choice(clbk: CallbackQuery) -> None:
    await clbk.answer()
    await clbk.message.answer(
        SHOP_CHOICE_MESSAGE,
        reply_markup=tabs.shop_choice,
    )


@router.callback_query(F.data == Navigation.in_shop.common)
async def show_common_shop(clbk: CallbackQuery) -> None:
    await clbk.answer()
    await clbk.message.answer(
        COMMON_SHOP_MESSAGE,
        reply_markup=tabs.common_shop,
    )


@router.callback_query(F.data == Navigation.in_shop.special)
async def show_special_shop(clbk: CallbackQuery) -> None:
    await clbk.answer()
    await clbk.message.answer(
        SPECIAL_SHOP_MESSAGE,
        reply_markup=tabs.special_shop,
    )


@router.callback_query(F.data == Navigation.in_shop.donut)
async def show_donut(clbk: CallbackQuery) -> None:
    await clbk.answer()
    await clbk.message.answer(
        DONUT_MESSAGE,
        reply_markup=tabs.donut_shop,
    )
