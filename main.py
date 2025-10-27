# import asyncio
import uvicorn

from fastapi import FastAPI

# from src.core.settings import config
# from src.handlers.telegram.app.debug import router as tg_router
from src.core.startup_configure import lifespan
from src.handlers.api.router import router as api_router


app = FastAPI(debug=True, lifespan=lifespan)
app.title = "YUQA"
app.include_router(router=api_router, prefix="/view")


def main():
    # dp = config.dp
    # bot = config.bot
    # dp.include_router(router=tg_router)
    # asyncio.create_task(dp.start_polling(bot))

    uvicorn.run(app="main:app", host="127.0.0.1", port=8099, reload=True)


if __name__ == "__main__":
    main()
