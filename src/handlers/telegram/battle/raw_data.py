from src.handlers.telegram.constants import user_data


ERROR_START_CMD_WITHOUT_ARGUMENTS = "called _cmd_start without callback and user id!"

ATTACK_BUTTON = "🗡 Атака ({})"
BLOCK_BUTTON = "🛡 Блок ({})"
BONUS_BUTTON = "⭐ Бонус ({})"
ABILITY_BUTTON = "🌀 Способность"
CHANGE_CARD_BUTTON = "🔀 Сменить персонажа"
CHANGE_TARGET_BUTTON = "㊗️ Сменить цель"
SHOW_DECK_BUTTON = "👤 своя колода"
SHOW_OPPOENT_BUTTON = "👁️‍🗨️ колода соперника"
END_ROUND_BUTTON = "✅ Завершить ход"


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
