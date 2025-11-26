from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()

class GameStates(StatesGroup):
    waiting_for_action = State()
    changing_character = State()

user_data = {}

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """Инициализация игры"""
    user_id = message.from_user.id
    
    # Инициализация данных пользователя
    user_data[user_id] = {
        'action_score': 3,
        'attack_count': 0,
        'block_count': 0, 
        'bonus_count': 0,
        'ability_used': False,
        'current_character': 1
    }
    
    await state.set_state(GameStates.waiting_for_action)
    await show_action_keyboard(message, user_id)

async def show_action_keyboard(message: Message, user_id: int):
    """Показать клавиатуру с действиями"""
    builder = InlineKeyboardBuilder()
    
    # Получаем данные пользователя
    data = user_data[user_id]
    
    # Кнопки действий (всегда активны, если есть ходы)
    if data['action_score'] > 0:
        builder.button(text=f"🗡 Атака ({data['attack_count']})", callback_data="action_attack")
        builder.button(text=f"🛡 Блок ({data['block_count']})", callback_data="action_block")
        builder.button(text=f"⭐ Бонус ({data['bonus_count']})", callback_data="action_bonus")
        builder.button(text=f"🌀 Способность", callback_data="action_ability")
    
    # Кнопка смены персонажа (всегда активна)
    builder.button(text="🔀 Сменить персонажа", callback_data="action_change_character")
    
    # Завершение хода (когда ходы закончились)
    if data['action_score'] <= 0:
        builder.button(text="✅ Завершить ход", callback_data="action_end_turn")
    
    builder.adjust(2, 2, 1, 1)  # Разметка кнопок
    
    # Текст статуса
    status_text = generate_status_text(user_id)
    
    # Отправляем или обновляем сообщение
    if 'message_id' in data:
        try:
            await message.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=data['message_id'],
                text=status_text,
                reply_markup=builder.as_markup()
            )
            return
        except:
            pass
    
    # Если сообщения нет или редактирование не удалось - отправляем новое
    msg = await message.answer(status_text, reply_markup=builder.as_markup())
    user_data[user_id]['message_id'] = msg.message_id

def generate_status_text(user_id: int) -> str:
    """Генерация текста статуса"""
    data = user_data[user_id]
    return (
        f"🎮 **Ход игрока**\n"
        f"👤 Персонаж: #{data['current_character']}\n"
        f"🎯 Осталось ходов: {data['action_score']}\n"
        f"🗡 Атак: {data['attack_count']} | "
        f"🛡 Блоков: {data['block_count']} | "
        f"⭐ Бонусов: {data['bonus_count']}\n"
        f"🌀 Способность: {'ИСПОЛЬЗОВАНА' if data['ability_used'] else 'доступна'}\n"
        f"\nВыберите действие:"
    )

@router.callback_query(F.data.startswith("action_"), GameStates.waiting_for_action)
async def process_action(callback: CallbackQuery, state: FSMContext):
    """Обработка действий игрока"""
    user_id = callback.from_user.id
    data = user_data[user_id]
    action = callback.data
    
    # Проверяем остались ли ходы (кроме смены персонажа)
    if data['action_score'] <= 0 and action != "action_change_character":
        await callback.answer("Ходы закончились! Завершите ход или смените персонажа", show_alert=True)
        return
    
    # Обработка разных действий
    if action == "action_attack":
        data['attack_count'] += 1
        data['action_score'] -= 1
        await callback.answer("🗡 Атака добавлена!")
        
    elif action == "action_block":
        data['block_count'] += 1
        data['action_score'] -= 1
        await callback.answer("🛡 Блок добавлен!")
        
    elif action == "action_bonus":
        data['action_score'] += 1
        data['action_score'] -= 1
        await callback.answer("⭐ Бонус добавлен!")
        
    elif action == "action_ability":
        if data['ability_used']:
            await callback.answer("Способность уже использована!", show_alert=True)
            return
        data['ability_used'] = True
        data['action_score'] -= 1
        await callback.answer("🌀 Способность активирована!")
        
    elif action == "action_change_character":
        await show_character_selection(callback.message, user_id)
        await callback.answer()
        return
        
    elif action == "action_end_turn":
        await end_turn(callback.message, user_id)
        await callback.answer()
        return
    
    # Обновляем клавиатуру
    await show_action_keyboard(callback.message, user_id)

async def show_character_selection(message: Message, user_id: int):
    """Показать выбор персонажа"""
    builder = InlineKeyboardBuilder()
    
    # Кнопки выбора персонажа
    for i in range(1, 6):
        builder.button(text=f"Персонаж #{i}", callback_data=f"character_{i}")
    
    # Кнопка назад
    builder.button(text="🔙 Назад", callback_data="character_back")
    builder.adjust(2, 2, 1, 1)
    
    await message.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=user_data[user_id]['message_id'],
        text="👥 **Выбор персонажа**\nВыберите персонажа (1-5):",
        reply_markup=builder.as_markup()
    )

@router.callback_query(F.data.startswith("character_"))
async def process_character_selection(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора персонажа"""
    user_id = callback.from_user.id
    
    if callback.data == "character_back":
        # Возврат к основному меню
        await show_action_keyboard(callback.message, user_id)
        await callback.answer()
        return
    
    # Извлекаем номер персонажа
    character_num = int(callback.data.split("_")[1])
    user_data[user_id]['current_character'] = character_num
    
    await callback.answer(f"Персонаж #{character_num} выбран!")
    await show_action_keyboard(callback.message, user_id)

async def end_turn(message: Message, user_id: int):
    """Завершение хода"""
    data = user_data[user_id]
    
    # Здесь можно добавить логику обработки завершённого хода
    summary_text = (
        f"🎯 **Ход завершён!**\n"
        f"Итоги:\n"
        f"🗡 Атак: {data['attack_count']}\n"
        f"🛡 Блоков: {data['block_count']}\n" 
        f"⭐ Бонусов: {data['bonus_count']}\n"
        f"🌀 Способность: {'ИСПОЛЬЗОВАНА' if data['ability_used'] else 'не использована'}\n"
        f"👤 Персонаж: #{data['current_character']}"
    )
    
    await message.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=data['message_id'],
        text=summary_text
    )
    
    # Сброс данных для следующего хода (или можно сохранить историю)
    reset_user_turn(user_id)

def reset_user_turn(user_id: int):
    """Сброс данных хода пользователя"""
    user_data[user_id].update({
        'action_score': 3,
        'attack_count': 0,
        'block_count': 0,
        'bonus_count': 0,
        'ability_used': False
        # current_character сохраняется
    })