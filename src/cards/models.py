from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional, Iterable

from sqlalchemy import JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.BaseModel import Base


class MCard(Base):
    __tablename__ = "cards"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    name: Mapped[int] = mapped_column(unique=True)

    universe: Mapped[str] = mapped_column()
    rarity: Mapped[str] = mapped_column()
    image: Mapped[str] = mapped_column()

    ability_id: Mapped[int] = mapped_column("abilities.id", nullable=True)
    description: Mapped[str] = mapped_column()

    class_: Mapped[str] = mapped_column()

    atk: Mapped[int] = mapped_column()
    hp: Mapped[int] = mapped_column()
    def_: Mapped[int] = mapped_column()


class MAbilities(Base):
    __tablename__ = "abilities"

    id: Mapped[int] = mapped_column(primary_key=True)
    sub_abilities: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        doc="annotated SubAbility as json(dict)"
    )
    card_id: Mapped[int] = mapped_column("users_t.id", unique=True)
    cooldown: Mapped[int] = mapped_column()
    duration: Mapped[int] = mapped_column()
    cost: Mapped[int] = mapped_column()


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
    id: Optional[int] = None
    name: Optional[str] = None
    universe: Optional[str] = None
    rarity: Optional[Rarity] = None
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
