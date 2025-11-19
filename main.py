import asyncio

from fastapi import FastAPI
import uvicorn

#  from aiohttp import web

from src.core.settings import config
from src.core.startup_configure import on_shutdown, on_startup
from src.handlers.telegram.router import router
from src.handlers.api.router import router

app = FastAPI(debug=True)
app.include_router(router)
async def main():
    # dp = config.dp

    # dp.include_router(router)
    await on_startup()
    await on_shutdown()

    
    
    uvicorn.run("main:app", reload=True)
    # await dp.start_polling(config.bot) # type: ignore
    # app = create_web_app()
    # web.run_app(
    #     app,
    #     host=config.LOCAL_WEBAPP_HOST,
    #     port=config.LOCAL_WEBAPP_PORT,
    # )

if __name__ == "__main__":
    asyncio.run(main())