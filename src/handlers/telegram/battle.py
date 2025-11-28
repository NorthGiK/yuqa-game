from types import NoneType
from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from fastapi import APIRouter, HTTPException

from datetime import datetime
from typing import Any, Collection, Optional
from pydantic import BaseModel
from aiogram.types import Message
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.battles.logic.domain import Battle_T, BattlesManagement
from src.core.settings import config
from src.battles.logic.process import start_battle
from src.battles.models import BattleType
from src.battles.schemas import SStandardBattleChoice
from src.constants import BattleInProcessOrEnd, BattleState
from src.database.core import AsyncSessionLocal
from src.handlers.rabbit.constants import INIT_BATTLE_QUEUE
from src.handlers.rabbit.core import rabbit
from src.utils.redis_cache import redis
from src.handlers.telegram.constants import BattleChoiceTG, GameStates, user_data
from src.logs import get_logger, dev_configure
from src.users.models import MUser


router = Router()
api_router = APIRouter()

log = get_logger(__name__)
dev_configure()

class User(BaseModel):
    rating: int
    inventory: list[int]
    deck: list[int]
    created_at: datetime
    active: bool = True


@api_router.post("/create_user")
async def create_user_handler(data: User):
    if data.inventory == [0]:
        data.inventory = [1, 2]
    if data.deck == [0]:
        data.deck = [1,2]

    user = MUser(**data.model_dump())
    async with AsyncSessionLocal() as session:
        session.add(user)
        await session.commit()

    return "OK"


@api_router.post("/start_battle")
async def start_duo_battle_api(
    user_id: int,
    type: str,
) -> Optional[bool]:
    return await start_battle(user_id=user_id, type=type)


@api_router.post("/process_battle")
async def handle_user_step(
		choice: SStandardBattleChoice,
	) -> Optional[BattleInProcessOrEnd]:
    battle = BattlesManagement.get_battle(choice.battle_id)
    if battle is None:
        return None

    used_bonus: int = sum((choice.hits, choice.blocks, choice.bonus))
    user_action_score: int = battle.get_user(choice.user_id).action_score #type:ignore

    if used_bonus > user_action_score:
        raise HTTPException(401, "too much used bonus!")
    elif used_bonus < user_action_score:
        raise HTTPException(401, "too few used bonus!")

    return battle.add_step(choice=choice)


@router.message(F.text == "Дуо")
async def start_duo_battle(msg: Message) -> None:
    user_id: int = msg.from_user.id

    await start_battle(user_id=user_id, type=BattleType.duo)


@rabbit.subscriber(INIT_BATTLE_QUEUE)
async def confirm_battle(users: Collection[int]) -> None:
    for user in users:
        if not await redis.get(f"battle:{user}"):
            raise Exception("don't found user in battle!\n"
                            f"user id: `{user}`"
                            )
    
    for user in users:
        await config.tg_workflow.bot.send_message(
            user,
            "***бой найден!*** согласен начать его?",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [ InlineKeyboardButton(text="Да!", callback_data="init_battle_in_tg") ]
            ]),
            parse_mode="markdown",
        )


async def _cmd_start(
        clbk: Message | CallbackQuery,
        state: FSMContext,
        *,
        params: dict[str, Any] | None = None,
    ) -> None:
    """Инициализация игры"""
    user_id: int = clbk.from_user.id

    # Инициализация данных пользователя
    user_data[user_id] = BattleChoiceTG(**({} if not params else params))
    log.info("create new battle choice with id {id}".format(id=user_id))

    await state.set_state(GameStates.waiting_for_action)
    log.info("state is seted")

    await show_action_keyboard(clbk, user_id)
    log.info("showing action keyboard")


@router.callback_query(F.data == "init_battle_in_tg")
async def cmd_start_handler(
    clbk: CallbackQuery | Message,
    state: FSMContext,
    /,
    params: dict[str, Any] | None = None
) -> None:
    return await _cmd_start(clbk, state, params=params)


async def show_action_keyboard(clbk: CallbackQuery | Message, user_id: int):
    """Показать клавиатуру с действиями"""
    if isinstance(clbk, CallbackQuery):
        await clbk.answer()

    builder = InlineKeyboardBuilder()

    # Получаем данные пользователя
    data = user_data[user_id]

    # Кнопки действий (всегда активны, если есть ходы)
    if data.action_score > 0:
        builder.button(text=f"🗡 Атака ({data.attack_count})", callback_data="action_attack")
        builder.button(text=f"🛡 Блок ({data.block_count})", callback_data="action_block")
        builder.button(text=f"⭐ Бонус ({data.bonus_count})", callback_data="action_bonus")
        builder.button(text=f"🌀 Способность", callback_data="action_ability")

    # Кнопка смены персонажа (всегда активна)
    builder.button(text="🔀 Сменить персонажа", callback_data="action_change_character")

    # Завершение хода (когда ходы закончились)
    if data.action_score <= 0:
        builder.button(text="✅ Завершить ход", callback_data="action_end_turn")

    builder.adjust(2, 2, 1, 1)  # Разметка кнопок

    # Текст статуса
    status_text = generate_status_text(user_id)

    # Отправляем или обновляем сообщение
    if data.message_id is not None:
        try:
            await clbk.bot.edit_message_text(
                chat_id=clbk.from_user.id,
                message_id=data.message_id,
                text=status_text,
                reply_markup=builder.as_markup(),
            )
            return
        except:
            pass

    # Если сообщения нет или редактирование не удалось - отправляем новое
    if isinstance(clbk, CallbackQuery):
        if clbk.message is None:
            raise Exception("message is None!! fuck blyat!")
        msg = await clbk.message.answer(status_text, reply_markup=builder.as_markup())

    else:
        msg = await clbk.answer(status_text, reply_markup=builder.as_markup())

    user_data[user_id].message_id = msg.message_id

def generate_status_text(user_id: int) -> str:
    """Генерация текста статуса"""
    data = user_data[user_id]
    return (
        f"🎮 **Ход игрока**\n"
        f"👤 Персонаж: #{data.current_character}\n"
        f"🎯 Осталось ходов: {data.action_score}\n"
        f"🗡 Атак: {data.attack_count} | "
        f"🛡 Блоков: {data.block_count} | "
        f"⭐ Бонусов: {data.bonus_count}\n"
        f"🌀 Способность: {'ИСПОЛЬЗОВАНА' if data.ability_used else 'доступна'}\n"
        f"\nВыберите действие:"
    )


@router.callback_query(F.data.startswith("action_"), GameStates.waiting_for_action)
async def process_action(callback: CallbackQuery, state: FSMContext) -> None:
    """Обработка действий игрока"""
    user_id: int = callback.from_user.id
    data: BattleChoiceTG = user_data[user_id]
    action: Optional[str] = callback.data
    if action is None:
        log.warning("can't get action from {file}".format(file=__file__))
        return None

    # Проверяем остались ли ходы (кроме смены персонажа)
    if data.action_score <= 0 and action != "action_change_character":
        await callback.answer("Ходы закончились! Можешь смените персонажа", show_alert=True)
        await end_turn(callback.message, user_id)
        return

    # Обработка разных действий
    if action == "action_attack":
        data.attack_count += 1
        data.action_score -= 1
        await callback.answer("🗡 Атака добавлена!")

    elif action == "action_block":
        data.block_count += 1
        data.action_score -= 1
        await callback.answer("🛡 Блок добавлен!")

    elif action == "action_bonus":
        data.action_score += 1
        data.action_score -= 1
        await callback.answer("⭐ Бонус добавлен!")

    elif action == "action_ability":
        if data.ability_used:
            await callback.answer("Способность уже использована!", show_alert=True)
            return

        data.ability_used = True
        data.action_score -= 5
        await callback.answer("🌀 Способность активирована!")

    elif action == "action_change_character":
        current_card = user_data[user_id].current_character
        await show_character_selection(callback.message, user_id, current_card)
        await callback.answer()
        return

    elif action == "action_end_turn":
        await callback.answer()
        await end_turn(callback.message, user_id)
        return

    # Обновляем клавиатуру
    await show_action_keyboard(callback, user_id)


async def show_character_selection(message: Message, user_id: int, current_character: int) -> None:
    """Показать выбор персонажа"""
    builder = InlineKeyboardBuilder()
    battle_id = await redis.get(f"battle:{user_id}")
    battle = BattlesManagement.get_battle(battle_id.decode())
    if battle is None:
        return

    # Кнопки выбора персонажа
    for i, card in enumerate(battle.get_deck_by_user(user_id), 1):
        if i == current_character:
            continue

        builder.button(text=f"Персонаж #{i} {card.name}", callback_data=f"character_{i}")

    # Кнопка назад
    builder.button(text="🔙 Назад", callback_data="character_back")
    builder.adjust(2, 2, 1, 1)

    await message.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=user_data[user_id].message_id,
        text="👥 **Выбор персонажа**\nВыберите персонажа (1-5):",
        parse_mode="markdown",
        reply_markup=builder.as_markup()
    )

@router.callback_query(F.data.startswith("character_"))
async def process_character_selection(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора персонажа"""
    user_id = callback.from_user.id

    if callback.data == "character_back":
        # Возврат к основному меню
        await show_action_keyboard(callback, user_id)
        await callback.answer()
        return

    # Извлекаем номер персонажа
    character_num = int(callback.data.split("_")[-1])
    user_data[user_id].current_character = character_num

    await callback.answer(f"Персонаж #{character_num} выбран!")
    await show_action_keyboard(callback.message, user_id)


async def end_turn(message: Message, user_id: int):
    """Завершение хода"""
    data: BattleChoiceTG = user_data[user_id]
    battle_id: Optional[bytes] = await redis.get(f"battle:{user_id}")
    battle = BattlesManagement.get_battle((bid := battle_id) if isinstance(bid, str) else bid.decode())
    status = battle.add_step(SStandardBattleChoice(**data.asdict))

    if (status == BattleState.global_.end) or (status == BattleState.local.end):
        await start_new_turn(message, battle)

    summary_text = (
        f"🎯 **Ход завершён!**\n"
        f"Итоги:\n"
        f"🗡 Атак: {data.attack_count}\n"
        f"🛡 Блоков: {data.block_count}\n" 
        f"⭐ Бонусов: {data.bonus_count}\n"
        f"🌀 Способность: {'ИСПОЛЬЗОВАНА' if data.ability_used else 'не использована'}\n"
        f"👤 Персонаж: #{data.current_character}"
    )

    await message.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=data.message_id,
        text=summary_text,
        parse_mode="markdown",
    )

    # Сброс данных для следующего хода (или можно сохранить историю)
    reset_user_turn(user_id)


async def start_new_turn(msg: Message, state: FSMContext, battle: Battle_T):
    users = battle.get_users()
    bot = config.tg_workflow.bot

    for user in users:
        deck_info = "\n"
        deck = battle.get_deck_by_user(user)
        deck_info.join(f"{i}. {card.name} | {card.hp}♥️ {card.atk}⚔️ {card.def_}🛡️ |" for i, card in enumerate(deck, 1))

        await bot.send_message(user.id, deck_info)
        await cmd_start(msg, state, params={})


def reset_user_turn(user_id: int):
    """Сброс данных хода пользователя"""
    user_data[user_id] = BattleChoiceTG(
        action_score = 3,
        attack_count = 0,
        block_count = 0,
        bonus_count = 0,
        ability_used = False,
        # current_character сохраняется
    )
