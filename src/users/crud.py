from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.core import get_db
from src.users.models import MUser


async def check_user(id: int) -> bool: # type: ignore
    db_session: AsyncSession = await get_db()
    query = select(MUser.id).where(MUser.id == id)
    user: Optional[int] = (await db_session.execute(query)).scalar_one_or_none()

    return bool(user)


async def create_user(id: int) -> bool:
    exist: bool = await check_user(id)
    if exist:
        return False

    db_session: AsyncSession = await get_db()

    new_user = MUser(id=id, role="tim")

    db_session.add(new_user)
    await db_session.commit()

    return True
  

async def delete_user(id: int) -> bool:
  db_session: AsyncSession = await get_db()
  query = select(MUser).where(MUser.id == id)
  user: Optional[MUser] = (await db_session.execute(query)).scalar_one_or_none()
  if user is None:
    return False

  await db_session.delete(user)
  await db_session.commit()
  return True