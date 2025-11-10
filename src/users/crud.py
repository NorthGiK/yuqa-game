from typing import Optional

from sqlalchemy import select

from src.database.core import AsyncSessionLocal
from src.users.models import MUser


async def check_user(id: int) -> bool:
    stmt = select(MUser.id).where(MUser.id == id)
    async with AsyncSessionLocal() as db_session:
        print("*\n" * 10)
        print("from check!")
        print()
        user: Optional[int] = (await db_session.execute(stmt)).scalar_one_or_none()

    return bool(user)


async def get_user(id: int) -> Optional[MUser]:
    stmt = select(MUser).where(MUser.id == id)

    async with AsyncSessionLocal() as db_session:
        user: Optional[MUser] = (await db_session.execute(stmt)).scalar_one_or_none()

    return user


async def create_user(id: int) -> bool:
    exist: bool = await check_user(id)
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
  

async def delete_user(id: int) -> bool:
    query = select(MUser).where(MUser.id == id)

    async with AsyncSessionLocal() as db_session:
        user: Optional[MUser] = (await db_session.execute(query)).scalar_one_or_none()
        if user is None:
            return False

        await db_session.delete(user)
        await db_session.commit()

    return True