from dataclasses import dataclass


@dataclass
class SBaseChoice:
    user_id: int
    battle_id: str

    hits: int
    blocks: int
    bonus: int


@dataclass(slots=True)
class SStandardBattleChoice(SBaseChoice):
    target: int
    selected_card: int
    ability: bool
