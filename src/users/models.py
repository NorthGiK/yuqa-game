from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.BaseModel import Base
from src.game_events.battle_pass.models import MPassProgress
from src.users.constants import (
    DEFAULT_USER_CARDS_IN_DECK,
    DEFAULT_USER_CARDS_IN_INVENTORY,
)
from src.users.types import CardId, Counts


def get_time() -> datetime:
    return datetime.now(timezone.utc)


class MUser(Base):
    __tablename__ = "users_t"

    id: Mapped[int] = mapped_column(primary_key=True)

    rating: Mapped[int] = mapped_column(insert_default=0)
    inventory: Mapped[dict[CardId, Counts]] = mapped_column(
        JSON,
        default=dict,
        insert_default=DEFAULT_USER_CARDS_IN_INVENTORY,
    )
    deck: Mapped[list[CardId]] = mapped_column(
        JSON,
        default=list,
        insert_default=DEFAULT_USER_CARDS_IN_DECK,
    )
    active: Mapped[bool] = mapped_column(
        insert_default=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=get_time,
    )

    pass_progress = relationship(
        "MPassProgress",
        uselist=False,
        back_populates="user",
        cascade="all, delete-orphan",
    )

    pytis: Mapped[int] = mapped_column(insert_default=0)
    coins: Mapped[int] = mapped_column(insert_default=0)
    wins: Mapped[int] = mapped_column(insert_default=0)
    draw: Mapped[int] = mapped_column(insert_default=0)
    loses: Mapped[int] = mapped_column(insert_default=0)


class MCardStorage(Base):
    __tablename__ = "card_storages"

    id: Mapped[int] = mapped_column(
        ForeignKey(MUser.id),
        primary_key=True,
    )
    copies_count: Mapped[dict[CardId, int]] = mapped_column(
        JSON,
        default=dict,
        insert_default=DEFAULT_USER_CARDS_IN_INVENTORY,
        doc="max count of copy is 0",
    )


class BattleResult(Enum):
    win = 1
    draw = 0
    loss = -1


@dataclass(slots=True, frozen=True)
class User:
    id: int

    rating: Optional[int] = 0
    inventory: Optional[list[int]] = None

    created_at: Optional[datetime] = None


@dataclass(slots=True, frozen=True)
class Profile:
    id: int

    username: str
    pytis: int
    coins: int
    created_at: datetime
    wins: int
    draw: int
    loses: int
