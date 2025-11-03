from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.database.core import init_db


async def on_startup() -> None:
  await init_db()
  
async def on_shutdown() -> None:
  ...

@asynccontextmanager
async def lifespan(app: FastAPI):
  await on_startup()
  yield
  await on_shutdown()