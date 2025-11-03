from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable, Optional

from sqlalchemy import text

from src.cards.exceptions import IncorrectTargetError


CREATE_CARD_TABLE = text("""
CREATE TABLE IF NOT EXISTS cards (
    id INT PRIMARY KEY,

    name VARCHAR,
    universe VARCHAR,
    rarity VARCHAR,
    description TEXT,

    ability INT,
    class VARCHAR,

    atk INT,
    hp INT,
    def_ INT
);
""")


CREATE_ABILITY_TABLE = text("""
CREATE TABLE IF NOT EXISTS abilities (
    id INT PRIMARY KEY,
    sub_abilities JSON,
    cards INT ARRAY,
    cooldown INT,
    duration INT,
    cost INT
);
""")

class Rarity(Enum):
    common = "ОБЫЧНАЯ"
    legendary = "ЛЕГЕНДАРНАЯ"
    badenko = "БАДЕНКО"


@dataclass(slots=True)
class MCard:
    id: int
    name: str
    universe: str
    rarity: Rarity
    description: str
    class_: ...
    atk: int
    hp: int
    def_: int
    pos: Optional[int] = field(default=None)


@dataclass(slots=True, frozen=True)
class Deck:
    cards: list[MCard]
    id: Optional[int] = field(default=None)


class AbilityType(Enum):
    damage = "atk"
    defense = "def_"
    hp = "hp"


@dataclass(frozen=True, slots=True)
class AbilityTarget:
    ownself: bool
    absolute: bool
    position: int

    def __post_init__(self) -> None:
        if self.ownself and self.absolute:
            raise IncorrectTargetError()


@dataclass(slots=True)
class SubAbility:
    type: AbilityType
    target: AbilityTarget
    value: int


@dataclass(slots=True)
class Ability:
    sub_abilities: Iterable[SubAbility]
    card_id: int
    cooldown: int
    duration: int
    cost: int