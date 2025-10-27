from typing import Annotated, AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import (
  create_async_engine, 
  async_sessionmaker, 
  AsyncSession,
)
from sqlalchemy.orm import DeclarativeBase

# from src.database.raw import loads_raw_card


class Base(DeclarativeBase):
  ...

engine = create_async_engine("sqlite+aiosqlite:///./db.sqlite3", echo=True)

AsyncSessionLocal = async_sessionmaker(
  bind=engine,
  expire_on_commit=False,
  class_=AsyncSession,
)

async def init_db():
  async with engine.connect() as conn:
    # conn.run_sync(Base.metadata.drop_all)
    await conn.run_sync(Base.metadata.drop_all)
    await conn.run_sync(Base.metadata.create_all)


async def _get_db_for_dep() -> AsyncGenerator[AsyncSession]:
  global AsyncSessionLocal
  async with AsyncSessionLocal() as session:
    yield session
      
async def get_db() -> AsyncSession:
  global AsyncSessionLocal
  async with AsyncSessionLocal() as session:
    return session

    
DBSession = Annotated[AsyncSession, Depends(_get_db_for_dep)]