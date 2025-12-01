from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.storage.memory import MemoryStorage
from fastapi import APIRouter, HTTPException

from datetime import datetime
from typing import Any, Collection, Optional
from pydantic import BaseModel
from aiogram.types import Message
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.battles.logic.common import CommonCardInBattle, CommonUserInBattle
from src.battles.logic.domain import Battle_T, BattlesManagement
from src.core.settings import Config, config
from src.battles.logic.process import start_battle
from src.battles.models import BattleType
from src.battles.schemas import SStandardBattleChoice
from src.constants import BattleInProcessOrEnd, BattleState
from src.database.core import AsyncSessionLocal
from src.handlers.rabbit.constants import INIT_BATTLE_QUEUE
from src.handlers.rabbit.core import rabbit
from src.handlers.telegram.battle.callbacks_data import ACTION_ABILITY, ACTION_ATTACK, ACTION_BLOCK, ACTION_BONUS, ACTION_CHANGE_CHARACTER, ACTION_CHANGE_TARGET, ACTION_END_TURN, ACTION_SHOW_DECK_STATUS, ACTION_SHOW_OPPONENT_STATUS
from src.handlers.telegram.battle.raw_data import ABILITY_BUTTON, ATTACK_BUTTON, BLOCK_BUTTON, BONUS_BUTTON, CHANGE_CARD_BUTTON, CHANGE_TARGET_BUTTON, END_ROUND_BUTTON, ERROR_START_CMD_WITHOUT_ARGUMENTS, SHOW_DECK_BUTTON, SHOW_OPPOENT_BUTTON, generate_status_text
from src.utils.redis_cache import redis
from src.handlers.telegram.constants import (
    USER_BATTLE_REDIS,
    BattleChoiceTG,
    GameStates,
    user_data,
)
from src.logs import get_logger, dev_configure
from src.users.models import MUser


router = Router()
api_router = APIRouter()

log = get_logger(__name__)
dev_configure()

async def delete_user_state(user_id: int) -> None:
    """Обновить данные пользователя"""
    storage = config.tg_workflow.storage
    bot = config.tg_workflow.bot

    key = StorageKey(chat_id=user_id, user_id=user_id, bot_id=bot.id)
    await storage.set_state(key=key)


async def create_battle_state(user_id: int) -> None:
    bot = config.tg_workflow.bot
    storage = config.tg_workflow.storage

    key = StorageKey(chat_id=user_id, user_id=user_id, bot_id=bot.id)
    await storage.set_state(key=key, state=GameStates.waiting_for_action)

@router.message(F.text == BattleType.duo)
async def start_duo_battle(msg: Message) -> None:
    user_id: int = msg.from_user.id

    await start_battle(user_id=user_id, type=BattleType.duo)


@rabbit.subscriber(INIT_BATTLE_QUEUE)
async def confirm_battle(users: Collection[int]) -> None:
    for user in users:
        await _cmd_start(user_id=user)


async def _cmd_start(
        clbk: Message | CallbackQuery | None = None,
        user_id: Optional[int] = None,
        state: Optional[FSMContext] = None,
    ) -> None:
    """Инициализация игры"""
    # Инициализация данных пользователя
    if (clbk is None) and (user_id is None):
        log.error(ERROR_START_CMD_WITHOUT_ARGUMENTS)
        return

    user_id = user_id if user_id else clbk.from_user.id
    if user_data.get(user_id) is None:
        user_data[user_id] = BattleChoiceTG()

    if state is None:
        await create_battle_state(user_id)
    await show_action_keyboard(clbk, user_id)


@router.callback_query(F.data == "init_battle_in_tg")
async def cmd_start_handler(
    clbk: CallbackQuery | Message,
) -> None:
    return await _cmd_start(clbk=clbk)


async def show_action_keyboard(clbk: CallbackQuery | Message | None, user_id: int):
    """Показать клавиатуру с действиями"""
    if isinstance(clbk, CallbackQuery):
        await clbk.answer()

    builder = InlineKeyboardBuilder()

    # Получаем данные пользователя
    data = user_data[user_id]

    # Кнопки действий (всегда активны, если есть ходы)
    if data.action_score > 0:
        builder.button(text=ATTACK_BUTTON.format(data.attack_count), callback_data=ACTION_ATTACK)
        builder.button(text=BLOCK_BUTTON.format(data.block_count), callback_data=ACTION_BLOCK)
        builder.button(text=BONUS_BUTTON.format(data.bonus_count), callback_data=ACTION_BONUS)
        builder.button(text=ABILITY_BUTTON, callback_data=ACTION_ABILITY)

    # Кнопка смены персонажа (всегда активна)
    builder.button(text=CHANGE_CARD_BUTTON, callback_data=ACTION_CHANGE_CHARACTER)
    builder.button(text=CHANGE_TARGET_BUTTON, callback_data=ACTION_CHANGE_TARGET)

    # Кнопка показа состояния колоды
    builder.button(text=SHOW_DECK_BUTTON, callback_data=ACTION_SHOW_DECK_STATUS)
    builder.button(text=SHOW_OPPOENT_BUTTON, callback_data=ACTION_SHOW_OPPONENT_STATUS)

    # Завершение хода (когда ходы закончились)
    if data.action_score <= 0:
        builder.button(text=END_ROUND_BUTTON, callback_data=ACTION_END_TURN)

    builder.adjust(2, 2, 2, 1, 1)  # Разметка кнопок

    # Текст статуса
    status_text = generate_status_text(user_id)

    # Отправляем или обновляем сообщение
    if data.message_id is not None:
        try:
            await Config().tg_workflow.bot.edit_message_text(
                chat_id=user_id,
                message_id=data.message_id,
                text=status_text,
                reply_markup=builder.as_markup(),
            )
            return
        except:
            pass

    # Если сообщения нет или редактирование не удалось - отправляем новое
    if isinstance(clbk, CallbackQuery):
        msg = await clbk.message.answer(status_text, reply_markup=builder.as_markup())

    elif isinstance(clbk, Message):
        msg = await clbk.answer(status_text, reply_markup=builder.as_markup())
    
    else:
        bot = Config().tg_workflow.bot
        msg = await bot.send_message(
            user_id,
            status_text,
            reply_markup=builder.as_markup(),
        )

    user_data[user_id].message_id = msg.message_id


async def show_character_selection(message: Message, user_id: int, current_character: int):
    battle_id_bytes: Optional[bytes] = await redis.get(f"battle:{user_id}")
    if not battle_id_bytes:
        return await message.answer("Бой не найден")

    battle = BattlesManagement.get_battle(battle_id_bytes.decode())
    if not battle:
        return await message.answer("Данные боя не найдены")

    deck = battle.get_deck_by_user(user_id)
    builder = InlineKeyboardBuilder()

    # Показываем только живых персонажей
    for i, card in enumerate(deck):
        if card.hp > 0 and i != current_character - 1:
            builder.button(
                text=f"Персонаж #{i+1} {card.name} (♥ {card.hp})", 
                callback_data=f"character_{i+1}"
            )

    if builder.buttons:
        builder.button(text="🔙 Назад", callback_data="character_back")
        builder.adjust(1)

        await message.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=user_data[user_id].message_id,
            text=f"👥 **Выбор персонажа**\nВыберите персонажа:",
            parse_mode="markdown",
            reply_markup=builder.as_markup(),
        )
    else:
        await message.answer("Нет доступных персонажей для смены")


async def show_target_selection(message: Message, user_id: int, current_character: int) -> None:
    """Показать выбор персонажа"""
    builder = InlineKeyboardBuilder()

    battle_id = await redis.get(f"battle:{user_id}")
    battle = BattlesManagement.get_battle(battle_id.decode())
    if battle is None:
        return

    opponent_id = next(user.id for user in battle.get_users() if user.id != user_id)

    # Кнопки выбора персонажа
    for i, card in enumerate(battle.get_deck_by_user(opponent_id), 1):
        if i == current_character:
            continue

        builder.button(text=f"Персонаж #{i} {card.name}", callback_data=f"character_{i}")

    # Кнопка назад
    builder.button(text="🔙 Назад", callback_data="character_back")
    builder.adjust(2, 2, 1, 1)

    await message.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=user_data[user_id].message_id,
        text="👥 **Выбор цель для атаки**\nВыберите персонажа:",
        parse_mode="markdown",
        reply_markup=builder.as_markup()
    )


async def show_target_selection(message: Message, user_id: int, current_character: int):
    battle_id_bytes: Optional[bytes] = await redis.get(f"battle:{user_id}")
    if not battle_id_bytes:
        return await message.answer("Бой не найден")

    battle = BattlesManagement.get_battle(battle_id_bytes.decode())
    if not battle:
        return await message.answer("Данные боя не найдены")

    deck = battle.get_deck_by_user(user_id)
    builder = InlineKeyboardBuilder()

    # Показываем только живых персонажей
    for i, card in enumerate(deck):
        if card.hp > 0 and i != current_character - 1:
            builder.button(
                text=f"Цель #{i+1} {card.name} (♥ {card.hp})", 
                callback_data=f"character_{i+1}"
            )

    if builder.buttons:
        builder.button(text="🔙 Назад", callback_data="character_back")
        builder.adjust(1)

        await message.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=user_data[user_id].message_id,
            text=f"🤯 **Выбор Цели**\nВыберите персонажа:",
            parse_mode="markdown",
            reply_markup=builder.as_markup(),
        )
    else:
        await message.answer("Нет доступных целeй для смены")


async def end_turn(message: Message, state: FSMContext, user_id: int):
    """Завершение хода"""
    data: Optional[BattleChoiceTG] = user_data.get(user_id)
    if data is None:
        log.warning("user isn't in battles")
        return
    battle_id: Optional[bytes] = await redis.get(f"battle:{user_id}")
    
    if battle_id is None:
        await message.answer("Ошибка: бой не найден")
        return

    battle = BattlesManagement.get_battle(battle_id.decode())
    if not battle:
        await message.answer("Ошибка: данные боя не найдены")
        return

    deck = battle.get_deck_by_user(user_id)
    card = deck[data.current_character - 1]

    # Передаем ход в логику боя
    battle_choice = SStandardBattleChoice(
        user_id,
        battle.id,
        data.attack_count,
        data.block_count,
        data.bonus_count,
        data.target_character,
        data.current_character,
        data.ability_used,
    )
    battle_status = battle.add_step(battle_choice)

    summary_text = (
        f"🎯 **Ход завершён!**\n"
        f"Итоги:\n"
        f"🗡 Атак: {data.attack_count}\n"
        f"🛡 Блоков: {data.block_count}\n" 
        f"⭐ Бонусов: {data.bonus_count}\n"
        f"🌀 Способность: {'ИСПОЛЬЗОВАНА' if data.ability_used else 'не использована'}\n"
        f"👤 Персонаж: #{data.current_character} - {card.name}"
    )

    # Отправляем итоги хода
    await message.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=data.message_id,
        text=summary_text,
        parse_mode="markdown",
    )

    # Проверяем статус боя
    if battle_status == BattleState.global_.end:
        # Бой завершен
        await handle_battle_end(message, battle, user_id, state)
    if battle_status == BattleState.local.end:
        # Начинаем новый раунд
        for user in battle.get_users():
            await start_new_turn(state, user.id, battle)


def make_deck_status_text(deck: list[CommonCardInBattle]) -> str:
    text: str = ""
    for i, card in enumerate(deck, 1):
        text += f"{i}. {card.name} | {card.hp}♥️ {card.atk}⚔️ {card.def_}🛡️\n"

    return text


async def start_new_turn(state: FSMContext, user_id: int, battle: Battle_T):
    """Начало нового хода"""
    bot = Config().tg_workflow.bot

    # Получаем актуальные данные о колоде
    deck = battle.get_deck_by_user(user_id)

    # получение кол-ва очков действия
    user = battle.get_user(user_id)
    action_score = user.action_score

    # Формируем информацию о колоде
    deck_info = "🃏 **Состояние колоды:**\n"
    deck_info += make_deck_status_text(deck)

    # Отправляем обновленную информацию о колоде
    await bot.send_message(user_id, deck_info, parse_mode="markdown")

    # Сбрасываем данные для нового хода
    await reset_user_turn(user_id, action_score)

    # Начинаем новый ход
    await _cmd_start(user_id=user_id, state=state)


async def handle_battle_end(
        message: Message,
        battle: Battle_T,
        user_id: int,
        state: FSMContext,
    ) -> None:
    """Обработка завершения боя"""
    # Определяем результат боя
    result = battle.check_cards_hp()
    if result is None:
        log.warning("called end of battle, when don't all users cards died!")        
        return

    users = list(battle.get_users())

    win_message = "🎉 **Победа!** Вы выиграли бой!"
    loss_message = "💔 **Поражение!** Вы проиграли бой."
    oppoennt_id: int = next(user for user in users if user.id != user_id).id

    if len(users) == 2:
        if result == user_id:
            text = loss_message

            await message.bot.send_message(
                oppoennt_id,
                win_message,
                parse_mode="markdown",
            )
        elif result != 0:
            text = win_message

            await message.bot.send_message(
                oppoennt_id,
                loss_message,
                parse_mode="markdown",
            )
        else:  # Ничья
            text = "🤝 **Ничья!**"
            await message.bot.send_message(
                oppoennt_id,
                text,
                parse_mode="markdown",
            )
    else:
        text = "⚔️ **Бой завершен!**"

    # Отправляем результат
    await message.bot.send_message(
        chat_id=message.chat.id,
        text=text,
        parse_mode="markdown"
    )

    # Очищаем данные боя
    for user in battle.get_users():
        del user_data[user.id]
        await redis.delete(USER_BATTLE_REDIS.format(id=user.id))
        await delete_user_state(user.id)


async def reset_user_turn(user_id: int, action_score: int = 0):
    """Сброс данных хода пользователя"""
    # Сохраняем текущего персонажа, цель, id последнего сообщения и обновляем очки действия, сбрасываем остальное
    current_char = user_data[user_id].current_character
    current_target = user_data[user_id].target_character

    battle_id: Optional[bytes] = await redis.get(USER_BATTLE_REDIS.format(id=user_id))
    if not battle_id:
        log.error("can't get battle id in %s from async def reset_user_turn", __file__)
        return None
    battle = BattlesManagement.get_battle(battle_id.decode())
    if battle is None:return

    own_deck: list[CommonCardInBattle] = battle.get_deck_by_user(user_id)

    opponent_id: int = battle.get_opponent(user_id).id
    opponent_deck: list[CommonCardInBattle] = battle.get_deck_by_user(opponent_id)

    def change_index(deck: list[CommonCardInBattle], current_index: int) -> int:
        for i, card in enumerate(deck):
            if card.hp > 0:
                current_index = i
                break

        return current_index


    current_char = change_index(own_deck, current_char)
    current_target = change_index(opponent_deck, current_target)
    user_data[user_id] = BattleChoiceTG(
        current_character=current_char + 1,
        target_character=current_target + 1,
        action_score=action_score,
        attack_count=0,
        block_count=0,
        bonus_count=0,
        ability_used=False
    )
