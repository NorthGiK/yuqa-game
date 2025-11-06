from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.sqlite import JSON

from src.database.BaseModel import Base


def get_date() -> datetime:
    return datetime.now(timezone.utc)


class MUser(Base):
    __tablename__ = "users_t"

    id: Mapped[int] = mapped_column(primary_key=True)

    rating: Mapped[int] = mapped_column(default=lambda: 0)
    inventory: Mapped[list[int]] = mapped_column(JSON, default=list)
    deck: Mapped[list[int]] = mapped_column(JSON, default=list)

    active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_date)


@dataclass(slots=True)
class User:
    id: int

    rating: Optional[int]
    inventory: Optional[list[int]]

    create_at: Optional[datetime]
