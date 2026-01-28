from .types import CardId, Counts

DEFAULT_USER_CARDS_IN_DECK: list[CardId] = [1, 2]
DEFAULT_USER_CARDS_IN_INVENTORY: dict[CardId, Counts] = {
    1: 1,
    2: 1,
}

USER_BATTLE_REWARD = 30
