from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Iterable

from pydantic import BaseModel, Field
from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column

from src.cards.exceptions import IncorrectTargetError
from src.database.BaseModel import Base


class MCard(Base):
    __tablename__ = "cards"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column() 
    universe: Mapped[str] = mapped_column()
    rarity: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()

    ability: Mapped[str] = mapped_column(JSON)
    class_: Mapped[str] = mapped_column()

    atk: Mapped[int] = mapped_column()
    hp: Mapped[int] = mapped_column()
    def_: Mapped[int] = mapped_column()


class MAbilities(Base):
    __tablename__ = "abilities"
    id: Mapped[int] = mapped_column(primary_key=True)
    sub_abilities: Mapped[str] = mapped_column(JSON)
    cards: Mapped[list[int]] = mapped_column(JSON)
    cooldown: Mapped[int] = mapped_column()
    duration: Mapped[int] = mapped_column()
    cost: Mapped[int] = mapped_column()


class Rarity(Enum):
    common = "ОБЫЧНАЯ"
    legendary = "ЛЕГЕНДАРНАЯ"
    badenko = "БАДЕНКО"


class CardInInventory(BaseModel):
    id: int
    name: str
    atk: int
    hp: int


class Card(BaseModel):
    id: int
    name: str
    universe: str
    rarity: Rarity
    description: str
    class_: str
    atk: int
    hp: int
    def_: int
    pos: Optional[int] = Field(default=None)


@dataclass(slots=True, frozen=True)
class Deck:
    cards: list[Card]
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