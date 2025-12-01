from dataclasses import dataclass
from typing import Optional

from sqlalchemy import select

from src.database.core import AsyncSessionLocal
from src.users.models import MUser


@dataclass(frozen=True, slots=True)
class UserRepository:
    db = AsyncSessionLocal

    @classmethod
    async def check_user(cls, id: int) -> bool:
        stmt = select(MUser.id).where(MUser.id == id)
        async with cls.db() as db_session:
            user: Optional[int] = (await db_session.execute(stmt)).scalar_one_or_none()

        return bool(user)


    @classmethod
    async def get_user(cls, id: int) -> Optional[MUser]:
        stmt = select(MUser).where(MUser.id == id)

        async with cls.db() as db_session:
            user: Optional[MUser] = (await db_session.execute(stmt)).scalar_one_or_none()

        return user
    

    @classmethod
    async def get_user_inventory(cls, id: int) -> Optional[list[int]]:
        stmt = select(MUser.deck).where(MUser.id == id)

        async with cls.db() as db:
            deck: Optional[list[int]] = (await db.execute(stmt)).scalar_one_or_none()
        
        return deck

    @classmethod
    async def add_new_card(cls, user_id: int, card_id: int) -> bool:
        stmt = select(MUser).where(MUser.id == user_id)
        async with cls.db() as db:
            user: Optional[MUser] = (await db.execute(stmt)).scalar_one_or_none()
            if not user:
                return False

            user.inventory.append(card_id)
            await db.refresh(user)
            await db.commit()

        return True


    @classmethod
    async def create_user(cls, id: int) -> bool:
        exist: bool = await cls.check_user(id)
        if exist:
            return False

        new_user = MUser(
            id=id,
            inventory=[1,2],
            deck=[1,2],
        )

        async with AsyncSessionLocal() as db_session:
            db_session.add(new_user)
            await db_session.commit()

        return True


    @classmethod
    async def delete_user(cls, id: int) -> bool:
        query = select(MUser).where(MUser.id == id)

        async with AsyncSessionLocal() as db_session:
            user: Optional[MUser] = (await db_session.execute(query)).scalar_one_or_none()
            if user is None:
                return False

            await db_session.delete(user)
            await db_session.commit()

        return True
