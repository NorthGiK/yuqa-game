from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.sqlite import JSON

from src.database.BaseModel import Base


CardId = int

def get_time() -> datetime:
    return datetime.now(timezone.utc)

class MUser(Base):
    __tablename__ = "users_t"

    id: Mapped[int] = mapped_column(primary_key=True)

    rating: Mapped[int] = mapped_column(insert_default=1)
    inventory: Mapped[list[CardId]] = mapped_column(
        JSON,
        default=list,
        insert_default=[1, 2],
    )
    deck: Mapped[list[CardId]] = mapped_column(
        JSON,
        default=list,
        insert_default=[1, 2],
    )

    active: Mapped[bool] = mapped_column(
        default=True,
        insert_default=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=get_time,
    )


class MCardStorage(Base):
    __tablename__ = "card_storages"

    id: Mapped[int] = mapped_column(
        ForeignKey(MUser.id),
        primary_key=True,
    )
    copies_count: Mapped[dict[CardId, int]] = mapped_column(
        JSON,
        default=dict,
        insert_default={1: 0, 2: 0},
        doc="max count of copy is 0"
    )


@dataclass(slots=True)
class User:
    id: int

    rating: Optional[int] = 0
    inventory: Optional[list[int]] = None

    created_at: Optional[datetime] = None
