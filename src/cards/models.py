from dataclasses import dataclass, field
from enum import Enum
from typing import Annotated, Iterable, List, Optional
from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.core import Base
from src.cards.exceptions import IncorrectTargetError


class MUniverse(Base):
    __tablename__ = "universes"
    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(unique=True)
    cards: Mapped[List["MCard"]] = relationship(back_populates="universe")


class MCard(Base):
    __tablename__ = "cards"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(unique=True)
    universe: Mapped[MUniverse] = relationship(back_populates="universes.cards")
    rarity: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()

    ability: Mapped['MAbility'] = relationship(back_populates="MAbility.card")
    class_: Mapped[str] = mapped_column()

    atk: Mapped[int] = mapped_column()
    hp: Mapped[int] = mapped_column()
    def_: Mapped[int] = mapped_column()


CREATE_CARD_TABLE = """
CREATE TABLE IF NOT EXISTS cards (
    id INT PRIMARY KEY,

    name VARCHAR,
    universe VARCHAR,
    rarity VARCHAR,
    description TEXT,

    ability FOREIGNKEY abilities.id,
    class VARCHAR,

    atk INT,
    hp INT,
    def_ INT
);
"""


CREATE_ABILITY_TABLE = """
CREATE TABLE IF NOT EXISTS abilities (
    id INT PRIMARY KEY,
    sub_abilities JSON,
    cards INT ARRAY,
    cooldown INT,
    duration INT,
    cost INT
);
"""

class Rarity(Enum):
    common = "ОБЫЧНАЯ"
    legendary = "ЛЕГЕНДАРНАЯ"
    badenko = "БАДЕНКО"


@dataclass(slots=True)
class MCard:
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
    cards: list[MCard]
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