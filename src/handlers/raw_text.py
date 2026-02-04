from datetime import date
from src.users.models import Profile


GREETING_NEW_USER_MESSAGE = "Добро пожаловать, пидр по имени {username}!"
GREETING_USER_MESSAGE = "Давное не виделись, пидр по имени {username}!"

BASE_USERNAME = "Игрок"

SHOW_INVENTORY_MESSAGE = "Посмотреть инвентарь"
BATTLE_CHOICE_MESSAGE = "Выбирай тип боя"
ADMIN_PANEL_MESSAGE = "🤏 Колдовская наху"

SHOP_CHOICE_MESSAGE = "Здарова, Меченый. Чего желаешь?"
COMMON_SHOP_MESSAGE = "Чекушки и макушки"
SPECIAL_SHOP_MESSAGE = "Дилдаки по скидкам и сосиски под расписку"
DONUT_MESSAGE = "чееееел, какой донат?\nхочешь деньги потратить, иди к админу в личку"


def PARSE_PROFILE_INFO(profile: Profile) -> str:
    """Создает соощение для показа пользователю его профиля"""
    created_at: date = profile.created_at
    return "\n".join(
            (
                f"Профиль {profile.username}",
                f"ID: {profile.id}",
                f"Miнеты: {profile.coins}",
                f"Создан: {created_at.day}.{created_at.month}.{created_at.year}",
                "--------",
                f"Победы: {profile.wins}",
                f"Ничьи: {profile.draw}",
                f"Поражения: {profile.loses}",
            )
        )
