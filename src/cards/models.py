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
    id: int
    name: str
    universe: str
    rarity: Rarity
    atk: int
    hp: int
    def_: int
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
    teammates = 3
    all = 4


@dataclass(slots=True)
class SubAbility:
    type: AbilityType
    target: TargetType
    value: int


@dataclass(slots=True)
class Ability:
    sub_abilities: Iterable[SubAbility]
    card_id: int
    cooldown: int
    duration: int
    cost: int
