from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import UserModel
from src.schemas.main import SGetUser


async def check_user(id: int, db_session: AsyncSession) -> bool:
  query = select(UserModel.id).where(UserModel.id == id)
  user: Optional[int] = (await db_session.execute(query)).scalar_one_or_none()

  return bool(user)


async def create_user(id: int, db_session: AsyncSession) -> bool:
  exist: bool = await check_user(id, db_session=db_session)
  if exist:
    return False
    
  new_user = UserModel(
    active=True,
    role="tim",
    id=id,
  )
  db_session.add(new_user)
  await db_session.commit()
  return True
  

async def delete_user(id: int, db_session: AsyncSession) -> bool:
  query = select(UserModel).where(UserModel.id == id)
  user: Optional[UserModel] = (await db_session.execute(query)).scalar_one_or_none()
  if user is None:
    return False
  
  await db_session.delete(user)
  await db_session.commit()
  return True