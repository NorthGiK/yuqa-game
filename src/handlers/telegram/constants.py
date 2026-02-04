from dataclasses import asdict, dataclass
from typing import Any, Optional

from aiogram.fsm.state import State, StatesGroup

BATTLE_ID_REDIS = "battle:{id}"
CURRENT_IVENTORY_PAGE_REDIS = "{user_id}:inventory:{rarity}"

@dataclass(frozen=True, slots=True, eq=False, init=False)
class Navigation:
    main = "MAIN"
    profile = "PROFILE"
    battle = "BATTLE"
    shop = "SHOP"
    gacha = "GACHA"
    inventory = "INVENTORY"
    tour = "TOUR"
    admin = "ADMIN"
    battle_pass = "BATTLE_PASS"

    @dataclass(frozen=True)
    class in_admin:
        create_universe = "CREATE UNIVERSE"
        create_card = "CREATE CARD"
        create_banner = "CREATE BANNER"

    @dataclass(frozen=True, slots=True)
    class in_inventory:
        legendary = "LEGENDARY"
        badenko = "BADENKO"

    @dataclass(frozen=True, slots=True)
    class in_battle:
        standard = "STANDARD"
        duo = "DUO"

    @dataclass(frozen=True, slots=True)
    class in_shop:
        common = "COMMON_SHOP"
        special = "SPECIAL_SHOP"
        donut = "DONUT"
    
    @dataclass(frozen=True, slots=True)
    class in_battle_pass:
        common = "COMMON_PASS"
        special = "SPECIAL_PASS"


user_data: dict[int, "BattleChoiceTG"] = {}


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
