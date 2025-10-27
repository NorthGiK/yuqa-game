from dataclasses import dataclass, field
from enum import Enum
import json
from typing import Annotated, Iterable, NamedTuple, Optional, TypeVar
from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.core import Base


class MCard(Base):
    __tablename__ = "cards"

    _prim_id: Mapped[int] = mapped_column(primary_key=True)

    name:        Mapped[str] = mapped_column(unique=True)
    universe:    Mapped[str] = mapped_column()
    rarity:      Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()

    ability: Mapped['Ability'] = relationship(back_populates="_prim_id")
    class_:  Mapped[str]       = mapped_column()

    atk:  Mapped[int] = mapped_column()
    hp:   Mapped[int] = mapped_column()
    def_: Mapped[int] = mapped_column()


class MAbility(Base):
    __tablename__ = 'abilities'

    _prim_id: Mapped[int] = mapped_column(primary_key=True)

    sub_abilities: Mapped[str]   = mapped_column()
    card:          Mapped[MCard] = relationship(back_populates="_prim_id")
    cooldown:      Mapped[int]   = mapped_column()
    duration:      Mapped[int]   = mapped_column()
    cost:          Mapped[int]   = mapped_column()


@dataclass
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


@dataclass
class Deck:
    cards: list[Card]
    id: Optional[Annotated[str, UUID]] = field(default=None)


class AbilityType(Enum):
    damage  = "atk"
    defense = "def_"
    hp = "hp"


@dataclass(frozen=True)
class AbilityTarget:
    ownself: bool
    absolute: bool
    position: int

    def __post_init__(self) -> None:
        if self.ownself and (self.absolute or self.position):
            raise 


@dataclass
class SubAbility:
    type:     AbilityType
    target:   AbilityTarget
    value:    int


    def json_dump(self) -> Annotated[str, "SubAbility"]:
        args_dicted = {
            "target": {
                "absolute": self.target.absolute,
                "position": self.target.position,
                "ownself": self.target.ownself,
            },
            "type": self.type.value,
            "value": self.value,
        }

        return json.dumps(args_dicted)


    @staticmethod
    def json_load(ability: Annotated[str, "SubAbility"]) -> "SubAbility":
        ability_dicted: dict = json.loads(ability)

        return SubAbility(
            type=ability_dicted['type'],
            target=AbilityTarget(**ability_dicted["target"]),
            value=ability_dicted['value'],
        )



@dataclass(frozen=True)
class Ability:
    sub_abilities: Iterable[SubAbility]
    card_id:       int
    cooldown:      int
    duration:      int
    cost:          int


    def json_dump(self) -> Annotated[str, "Ability"]:
        return json.dumps({
            "sub_abilities": [sub_ab.json_dump() for sub_ab in self.sub_abilities],
            "card_id": self.card_id,
            "cooldown": self.cooldown,
            "duration": self.duration,
            "cost": self.cost,
        })


    @staticmethod
    def json_load(ability: Annotated[str, "Ability"]) -> "Ability":
        ability_dicted = json.loads(ability)

        return Ability(
            sub_abilities=[sub_ab.json_load() for sub_ab in ability_dicted['sub_abilities']],
            card_id=ability_dicted["card_id"],
            cooldown=ability_dicted["cooldown"],
            duration=ability_dicted["duration"],
            cost=ability_dicted["cost"],
        )