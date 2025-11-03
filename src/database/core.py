from sqlalchemy.ext.asyncio import (
  	create_async_engine, 
	async_sessionmaker, 
	AsyncSession,
)

from src.database.BaseModel import Base


engine = create_async_engine("postgresql+asyncpg://yuqa:GitlerBest1488,@localhost/yuqa_db",
# "sqlite+aiosqlite:///db.sqlite3",
echo=True)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

async def init_db() -> None:
    async with engine.connect() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncSession:
    global AsyncSessionLocal
    async with AsyncSessionLocal() as session:
        return session