from dataclasses import asdict, dataclass
from typing import Any, Optional

from aiogram.fsm.state import State, StatesGroup


GET_USER_REDIS = "battle:{}"

@dataclass(frozen=True, slots=True)
class Navigation:
    main = "MAIN"
    profile = "PROFILE"
    battle = "BATTLE"
    shop = "SHOP"
    inventory = "INVENTORY"
    tour = "TOUR"

    @dataclass(frozen=True, slots=True)
    class in_inventory:
        legendary = "LEGENDARY"
        badenko = "BADENKO"
 

    @dataclass(frozen=True, slots=True)
    class in_battle:
        standard = "STANDARD"
        duo = "DUO"


user_data: dict[int, 'BattleChoiceTG'] = {}

class GameStates(StatesGroup):
    waiting_for_action = State()
    changing_character = State()


@dataclass(slots=True)
class BattleChoiceTG:
    action_score: int = 2
    attack_count: int = 0
    block_count: int = 0
    bonus_count: int = 0
    ability_used: bool = False
    current_character: int = 1
    target_character: int = 1
    message_id: Optional[int] = None

    @property
    def asdict(self) -> dict[str, Any]:
        return asdict(self)
