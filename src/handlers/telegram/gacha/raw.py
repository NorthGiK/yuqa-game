# ========RAW TEXT========
from src.cards.models import MCard


MAIN_GACHA_MESSAGE = "крути крутки, копи крутки, покупай крутки, заново всё это сделай"

def GETTING_CARD_MESSAGE(card: MCard) -> str:
    return (
        f"Тебе выпала карточка редкости: {card.rarity}~ !\n"
        f"Вселенная: {card.universe}\n"
        f"Имя: ¯\\_(ツ)_/¯ {card.name}\n"
        f"Здоровье {card.hp}❣️\n"
        f"Урон {card.atk}⚔️\n"
        f"Защита {card.def_}🛡️\n"
        "\n"
        f"класс: {card.class_}"
        "\n"
        f"{card.description}"
    )
