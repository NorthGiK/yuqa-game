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
    user_action_score: int = battle.get_user(user_id=choice.user_id).action_score #type:ignore

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
        exist_choice: Optional[BattleChoiceTG] = None,
    ) -> None:
    """Инициализация игры"""
    user_id: int = clbk.from_user.id

    # Инициализация данных пользователя
    user_data[user_id] = exist_choice or BattleChoiceTG()

    await state.set_state(GameStates.waiting_for_action)

    await show_action_keyboard(clbk, user_id)


@router.callback_query(F.data == "init_battle_in_tg")
async def cmd_start_handler(
    clbk: CallbackQuery | Message,
    state: FSMContext,
    params: dict[str, Any] | None = None
) -> None:
    return await _cmd_start(clbk, state)


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



@router.callback_query(F.data.startswith("action_"), GameStates.waiting_for_action)
async def process_action(callback: CallbackQuery, state: FSMContext) -> None:
    """Обработка действий игрока"""
    user_id: int = callback.from_user.id
    
    if user_id not in user_data:
        await callback.answer("Ошибка: данные не найдены", show_alert=True)
        return
    
    data: BattleChoiceTG = user_data[user_id]
    action: str = callback.data
    
    # Проверяем остались ли ходы (кроме смены персонажа и завершения хода)
    if data.action_score <= 0 and action not in ["action_change_character", "action_end_turn"]:
        await callback.answer("Ходы закончились! Завершите ход или смените персонажа", show_alert=True)
        return

    action_performed = True

    async def handle_action(
        attr: str,
        positive_message: str,
        else_message: str,
    ) -> None:
        if data.action_score > 0:
            data.action_score -= 1
            if (prev_value := getattr(data, attr)) is None:
                log.error(
                    "can't get attribute `%s` of `BattleChoiceTG`\n"
                    f"Error from `{__file__}` def process_action",
                    attr)

            setattr(data, attr, 1 + prev_value)
            await callback.answer(positive_message, show_alert=True)
        else:
            await callback.answer(else_message, show_alert=True)
            return    


    # Обработка разных действий
    if action == "action_attack":
        await handle_action(
            "attack_count",
            positive_message="🗡 Атака добавлена!",
            else_message="Недостаточно ходов для атаки!",
        )

    elif action == "action_block":
        await handle_action(
            "block_count", 
            "🛡 Блок добавлен!",
            "Недостаточно ходов для блока!",
        )

    elif action == "action_bonus":
        await handle_action(
            "bonus_count",
            "⭐ Бонус добавлен!",
            "Недостаточно ходов для бонуса!",
        )

    elif action == "action_ability":
        if data.ability_used:
            await callback.answer("Способность уже использована!", show_alert=True)
            return
        if data.action_score >= 5:  # Проверяем достаточно ли ходов для способности
            data.ability_used = True
            data.action_score -= 5
            await callback.answer("🌀 Способность активирована!")
        else:
            await callback.answer("Недостаточно ходов для способности! Нужно 5 ходов.", show_alert=True)
            return

    elif action == "action_change_character":
        current_card = data.current_character
        await show_character_selection(callback.message, user_id, current_card)
        await callback.answer()
        return

    elif action == "action_end_turn":
        await callback.answer()
        await end_turn(callback.message, state, user_id)
        return

    else:
        action_performed = False

    # Обновляем клавиатуру только если было выполнено действие
    if action_performed:
        await show_action_keyboard(callback, user_id)


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
        await handle_battle_end(message, battle, user_id)
    if battle_status == BattleState.local.end:
        # Начинаем новый раунд
        await start_new_turn(message, state, user_id, battle, battle_status)


async def start_new_turn(message: Message, state: FSMContext, user_id: int, battle: Battle_T, status: BattleInProcessOrEnd):
    """Начало нового хода"""
    bot = message.bot

    # Получаем актуальные данные о колоде
    deck = battle.get_deck_by_user(user_id)

    # Формируем информацию о колоде
    deck_info = "🃏 **Состояние колоды:**\n"
    for i, card in enumerate(deck, 1):
        deck_info += f"{i}. {card.name} | {card.hp}♥️ {card.atk}⚔️ {card.def_}🛡️\n"

    # Отправляем обновленную информацию о колоде
    await bot.send_message(user_id, deck_info, parse_mode="markdown")

    # Сбрасываем данные для нового хода
    reset_user_turn(user_id)

    # Начинаем новый ход
    await _cmd_start(message, state, user_data[user_id])


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

    users = battle.get_users()


    if len(users) == 2:
        if result == user_id:
            text = "🎉 **Победа!** Вы выиграли бой!"
        elif result == 0:  # Ничья
            text = "🤝 **Ничья!**"
        else:
            text = "💔 **Поражение!** Вы проиграли бой."
    else:
        text = "⚔️ **Бой завершен!**"

    # Отправляем результат
    await message.bot.send_message(
        chat_id=message.chat.id,
        text=text,
        parse_mode="markdown"
    )

    # Очищаем данные боя
    if user_id in user_data:
        del user_data[user_id]
    
    await state.set_state(None)
    await redis.delete(f"battle:{user_id}")


def reset_user_turn(user_id: int, action_score: int = 0):
    """Сброс данных хода пользователя"""
        # Сохраняем текущего персонажа, сбрасываем остальное
    current_char = user_data[user_id].current_character
    current_target = user_data[user_id].target_character
    user_data[user_id] = BattleChoiceTG(
        current_character=current_char,
        target_character=current_target,
        action_score=action_score,
        attack_count=0,
        block_count=0,
        bonus_count=0,
        ability_used=False
    )
