from datetime import date
from typing import Optional, Union

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message

from src.cards.crud import CardRepository
from src.cards.models import MCard, Rarity
from src.core.settings import Config
from src.handlers.raw_text import GREETING_NEW_USER_MESSAGE, GREETING_USER_MESSAGE
from src.handlers.telegram import constants
from src.handlers.telegram.components import tabs
from src.logs import dev_configure, get_logger
from src.users.crud import UserRepository
from src.utils.redis_cache import redis


router = Router()

log = get_logger(__name__)
dev_configure()


async def _start(msg: Union[Message, CallbackQuery]):
    user = msg.from_user
    if user is None:
        await msg.reply("чето не так с юзером, стань нормальным")  # type:ignore
        return

    username: Optional[str] = user.username
    user_id: int = user.id

    if not await UserRepository.check_user(user_id):
        await UserRepository.create_user(user_id)
        await msg.answer(
            GREETING_NEW_USER_MESSAGE.format(username=username),
            reply_markup=tabs.main,
        )
        return

    answer = dict(
        text=GREETING_USER_MESSAGE.format(username=username),
        reply_markup=tabs.admin_start
        if user_id == Config().tg_workflow.ADMIN_ID
        else tabs.main,
    )

    if isinstance(msg, CallbackQuery):
        await msg.answer()
        await msg.message.answer(**answer)
    else:
        await msg.answer(**answer)


@router.message(CommandStart())
async def start_handler(msg: Message):
    await _start(msg)


@router.callback_query(F.data == constants.Navigation.main)
async def main_handler(clbk: CallbackQuery):
    await _start(clbk)


@router.message(F.text == "Назад ↵")
async def back_to_main_handler(msg: Message) -> None:
    await _start(msg)


@router.callback_query(F.data == constants.Navigation.profile)
async def profile_handler(clbk: CallbackQuery):
    await clbk.answer("")

    profile = await UserRepository.get_profile(clbk.from_user.id)
    created_at: date = profile.created_at
    await clbk.message.answer(
        "\n".join((
            f"Профиль {clbk.from_user.username}",
            f"ID: {clbk.from_user.id}",
            f"Miнеты: {profile.coins}",
            f"Создан: {created_at.day}.{created_at.month}.{created_at.year}",
            "--------",
            f"Победы: {profile.wins}",
            f"Ничьи: {profile.draw}",
            f"Поражения: {profile.loses}",
        )),
        reply_markup=tabs.profile,
    )


async def _show_cards_for_rarity(
    clbk: CallbackQuery,
    rarity: Rarity,
) -> None:
    user_id: int = clbk.from_user.id
    cards: list[MCard] = await CardRepository.get_cards_by_rarity(
        rarity=rarity, user_id=user_id
    )

    page_num = int(await redis.get(f"inventory:{rarity.name}"))

    if page_num + 10 > len(cards):
        end = len(cards)
    else:
        end = page_num + 10

    cards = cards[page_num:end]

    await clbk.answer("")
    await clbk.message.answer(
        f"Инвентарь {clbk.from_user.username}",  # type:ignore
        reply_markup=tabs.in_inventory_create(cards),
    )  # type:ignore


@router.callback_query(F.data == Rarity.legendary.name)
async def legendary_cards_handler(clbk: CallbackQuery) -> None:
    await redis.setex(f"inventory:{Rarity.legendary.name}", 180, 0)
    return await _show_cards_for_rarity(clbk=clbk, rarity=Rarity.legendary)


@router.callback_query(F.data == constants.Navigation.inventory)
async def inventory_handler(clbk: CallbackQuery):
    await clbk.answer("")
    await clbk.message.answer(
        "Посмотреть инвентарь",
        reply_markup=tabs.inventory,
    )


@router.callback_query(F.data == constants.Navigation.battle)
async def battle_handler(clbk: CallbackQuery):
    await clbk.answer("ok")

    if clbk.message is None:
        return

    await clbk.message.answer(text="Выбирай тип боя", reply_markup=tabs.battle)


@router.callback_query(F.data == constants.Navigation.admin)
async def show_admin_panel(clbk: CallbackQuery) -> None:
    await clbk.answer()
    await clbk.message.answer(
        "🤏 Колдовская наху",
        reply_markup=tabs.admin_panel,
    )


@router.callback_query(F.data == constants.Navigation.shop)
async def show_shop_choice(clbk: CallbackQuery) -> None:
    await clbk.answer()
    await clbk.message.answer(
        "Здарова, Меченый. Чего желаешь?",
        reply_markup=tabs.shop_choice,
    )


@router.callback_query(F.data == constants.Navigation.in_shop.common)
async def show_common_shop(clbk: CallbackQuery) -> None:
    await clbk.answer()
    await clbk.message.answer(
        "Чекушки и макушки",
        reply_markup=tabs.common_shop,
    )


@router.callback_query(F.data == constants.Navigation.in_shop.special)
async def show_special_shop(clbk: CallbackQuery) -> None:
    await clbk.answer()
    await clbk.message.answer(
        "Дилдаки по скидкам и сосиски под расписку",
        reply_markup=tabs.special_shop,
    )


@router.callback_query(F.data == constants.Navigation.in_shop.donut)
async def show_donut(clbk: CallbackQuery) -> None:
    await clbk.answer()
    await clbk.message.answer(
        ("чееееел, какой донат?\nхочешь деньги потратить, иди к админу в личку"),
        reply_markup=tabs.donut_shop,
    )
