from typing import Optional
from sqlalchemy import JSON, select
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.BaseModel import Base
from src.database.core import AsyncSessionLocal
from src.game_events.battle_pass.constants import COMMON_PASS_STEP
from src.users.models import MUser


class MPassProgress(Base):
    __tablename__ = "special_pass"

    user: Mapped["MUser"] = relationship(
        "MUser",
        back_populates="pass_progress",
        uselist=False,
        cascade="all, delete-orphan",
    )

    tokens: Mapped[int] = mapped_column(insert_default=0)

    progress: Mapped[int] = mapped_column(insert_default=0)
    earned: Mapped[list[int]] = mapped_column(JSON, default=list, default_factory=lambda: [])


class PassRepository:
    db = AsyncSessionLocal

    @classmethod
    async def get_pass_by_id(cls, user_id: int) -> Optional[MPassProgress]:
        query = select(MUser.pass_progress).where(MUser.id == user_id)
        async with cls.db() as session:
            return (await session.execute(query)).scalar_one_or_none()

    @classmethod
    async def add_token(cls, user_id: int, tokens: int) -> None:
        query = select(MUser.pass_progress).where(MUser.id == user_id)
        async with cls.db() as session:
            mpass: Optional[MPassProgress] = (await session.execute(query)).scalar_one_or_none()
            if mpass is None:
                return

            added_progress = (mpass.tokens + tokens) // COMMON_PASS_STEP
            mpass.tokens += (mpass.tokens + tokens) % COMMON_PASS_STEP
            mpass.progress += added_progress

            await session.refresh(mpass, ("tokens", "progress"))
    