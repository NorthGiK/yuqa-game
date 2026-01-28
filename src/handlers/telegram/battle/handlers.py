from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from src.battles.logic.common import CommonCardInBattle, CommonUserInBattle
from src.battles.logic.domain import BattlesManagement
from src.handlers.telegram.battle.battle import end_turn, make_deck_status_text, show_action_keyboard, show_character_selection, show_target_selection
from src.handlers.telegram.constants import (
    BattleChoiceTG,
    GameStates,
    user_data,
)
from src.logs import get_logger, dev_configure


router = Router()
log = get_logger(__name__)
dev_configure()

@router.callback_query(F.data.startswith("show_"))
async def show_deck(clbk: CallbackQuery, state: FSMContext) -> None:
    """Обработка показа состояния колоды"""
    await clbk.answer()

    user_id: int = clbk.from_user.id
    battle = await BattlesManagement.get_battle_from_user(user_id)

    if clbk.data == "show_me":
        deck: list[CommonCardInBattle] = battle.get_deck_by_user(user_id)
        text: str = "🎴 **Твоя Колода:**\n"
    else:
        opponent: CommonUserInBattle = battle.get_opponent(user_id)
        deck: list[CommonCardInBattle] = battle.get_deck_by_user(opponent.id)
        text = "💢 **Колода Соперника:**\n"

    await clbk.bot.send_message(
        user_id,
        text + make_deck_status_text(deck),
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


@router.callback_query(F.data.startswith("target_"))
async def process_target_selection(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора персонажа"""
    user_id = callback.from_user.id

    if callback.data == "target_back":
        # Возврат к основному меню
        await show_action_keyboard(callback, user_id)
        await callback.answer()
        return

    # Извлекаем номер персонажа
    target_num = int(callback.data.split("_")[-1])
    user_data[user_id].target_character = target_num

    await callback.answer(f"Цель #{target_num} выбран!")
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
    if (
        data.action_score <= 0 and
        action not in [
            "action_change_character",
            "action_change_target",
            "show_me",
            "show_opponent",
            "action_end_turn",
        ]
    ):
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
            await callback.answer(positive_message)
        else:
            await callback.answer(else_message)
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

    elif action == "action_change_target":
        current_target = data.target_character
        await show_target_selection(callback.message, user_id, current_target)
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
