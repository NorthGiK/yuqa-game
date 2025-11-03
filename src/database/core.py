import asyncio

from sqlalchemy.ext.asyncio import (
  	create_async_engine, 
	async_sessionmaker, 
	AsyncSession,
)

from src.cards.models import CREATE_ABILITY_TABLE, CREATE_CARD_TABLE
from src.users.models import CREATE_USERS_TABLE
from src.battles.models import CREATE_BATTLE_QUEUE_TABLE


engine = create_async_engine(
    "postgresql+asyncpg://postgres:GitlerBest1488,@localhost/yuqa_database",
    echo=True,
)

class Ext_AsyncSession(AsyncSession):
    async def __del__(self) -> None:
        try:
            task = asyncio.create_task(self.close())
            await asyncio.shield(task)
        except:
            ...
    
    async def __delete__(self) -> None:
        try:
            task = asyncio.create_task(self.close())
            await asyncio.shield(task)
        except:
            ...


AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=Ext_AsyncSession,
)

async def init_db() -> None:
    async with engine.connect() as conn:
        await conn.execute(CREATE_CARD_TABLE)
        await conn.execute(CREATE_ABILITY_TABLE)
        await conn.execute(CREATE_USERS_TABLE)
        await conn.execute(CREATE_BATTLE_QUEUE_TABLE)


async def get_db() -> AsyncSession:
    global AsyncSessionLocal
    async with AsyncSessionLocal() as session:
        return session