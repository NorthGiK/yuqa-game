from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Iterable

from sqlalchemy import JSON, Column, ForeignKey, Integer, String, Text

from src.database.BaseModel import Base


class MCard(Base):
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, unique=True)

    universe = Column(String(50))
    rarity = Column(String(50))

    ability_id = Column(Integer, ForeignKey("abilities.id"), unique=True)
    description = Column(Text)

    class_ = Column(String)

    atk = Column(Integer)
    hp = Column(Integer)
    def_ = Column(Integer)


class MAbilities(Base):
    __tablename__ = "abilities"

    id = Column(Integer, primary_key=True)
    sub_abilities = Column(JSON)
    card_id = Column(Integer, ForeignKey("cards.id"), unique=True)
    cooldown = Column(Integer)
    duration = Column(Integer)
    cost = Column(Integer)


class Rarity(Enum):
    common = "ОБЫЧНАЯ"
    legendary = "ЛЕГЕНДАРНАЯ"
    badenko = "БАДЕНКО"


@dataclass(slots=True)
class Card:
    atk: int
    hp: int
    def_: int
    ability: 'Ability'
    id: int = None #type:ignore
    name: str = None #type:ignore
    universe: str = None #type:ignore
    rarity: Rarity = None #type:ignore
    pos: Optional[int] = field(default=None)


@dataclass(slots=True, frozen=True)
class Deck:
    cards: list[Card]
    id: Optional[int] = field(default=None)

    @property
    def get_card_ids(self) -> list[int]:
        return [card.id for card in self.cards]


class AbilityType(Enum):
    damage = "atk"
    defense = "def_"
    hp = "hp"


class TargetType(Enum):
    ownself = 1
    opponent = 2
    teammates_and_own = 3
    teammates_only = 4
    all = 5


@dataclass(slots=True, frozen=True)
class SubAbility:
    type: AbilityType
    target: TargetType
    value: int


@dataclass(slots=True)
class Ability:
    sub_abilities: Iterable[SubAbility]
    cooldown: int
    duration: int
    cost: int
    card_id: Optional[int] = None
