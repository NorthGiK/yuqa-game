from dataclasses import dataclass, field
from enum import Enum
from typing import Annotated, Iterable, Optional
from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.core import Base
from src.cards.exceptions import IncorrectTargetError


class MCard(Base):
    __tablename__ = "cards"

    _prim_id: Mapped[int] = mapped_column(primary_key=True)

    name:        Mapped[str] = mapped_column(unique=True)
    universe:    Mapped[str] = mapped_column()
    rarity:      Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()

    # ability: Mapped['Ability'] = relationship(back_populates="_prim_id")
    class_:  Mapped[str]       = mapped_column()

    atk:  Mapped[int] = mapped_column()
    hp:   Mapped[int] = mapped_column()
    def_: Mapped[int] = mapped_column()


class MAbility(Base):
    __tablename__ = 'abilities'

    _prim_id: Mapped[int] = mapped_column(primary_key=True)

    sub_abilities: Mapped[str]   = mapped_column()
    # card:          Mapped[MCard] = relationship(back_populates="_prim_id")
    cooldown:      Mapped[int]   = mapped_column()
    duration:      Mapped[int]   = mapped_column()
    cost:          Mapped[int]   = mapped_column()


class Rarity(Enum):
    common = "ОБЫЧНАЯ"
    legendary = "ЛЕГЕНДАРНАЯ"
    badenko = "БАДЕНКО"


@dataclass(slots=True)
class Card:
    id: int
    name: str
    universe: str
    rarity: str
    description: str
    class_: str
    atk: int
    hp: int
    def_: int
    pos: Optional[int] = field(default=None)


@dataclass(slots=True)
class Deck:
    cards: list[Card]
    id: Optional[Annotated[str, UUID]] = field(default=None)


class AbilityType(Enum):
    damage  = "atk"
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
    type:     AbilityType
    target:   AbilityTarget
    value:    int


@dataclass(frozen=True, slots=True)
class Ability:
    sub_abilities: Iterable[SubAbility]
    card_id:       int
    cooldown:      int
    duration:      int
    cost:          int