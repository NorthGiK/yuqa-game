from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.database.core import init_db
# from src.database.raw import loads_raw_card


async def on_startup() -> None:
  await init_db()
  # await loads_raw_card()
  # await redis
  
async def on_shutdown() -> None:
  ...

@asynccontextmanager
async def lifespan(app: FastAPI):
  await on_startup()
  yield
  await on_shutdown()