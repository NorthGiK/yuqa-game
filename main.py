import asyncio
import sys

from fastapi import FastAPI
import uvicorn

from src.core.startup_configure import lifespan, on_startup, on_shutdown
from src.handlers.telegram.router import router as tg_router
from src.handlers.api.router import router
from src.core.settings import config


app = FastAPI(debug=True, lifespan=lifespan, title="Yuqa", docs_url="/")
app.include_router(router)

async def web():
    uvicorn.run("main:app", reload=True)

async def telegram():
    dp = config.tg_workflow.dp
    bot = config.tg_workflow.bot
    await on_startup()

    dp.include_router(tg_router)

    await dp.start_polling(bot) #type:ignore

    await on_shutdown()


if __name__ == "__main__":
    if sys.argv[-1] == "--web":
        run = web()
    else:
        run =  telegram()
    
    asyncio.run(run)