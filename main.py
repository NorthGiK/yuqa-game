import asyncio

from src.core.settings import config
from src.core.startup_configure import on_shutdown, on_startup
from src.handlers.telegram.router import router


async def main():
    bot = config.bot
    dp = config.dp
    dp.include_router(router)

    await on_startup()
    await dp.start_polling(bot) #type:ignore
    await on_shutdown()


if __name__ == "__main__":
    asyncio.run(main())