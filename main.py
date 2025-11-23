import asyncio

from fastapi import FastAPI
import uvicorn

from src.core.startup_configure import on_shutdown, on_startup
from src.handlers.telegram.router import router
from src.handlers.api.router import router


app = FastAPI(debug=True, title="Yuqa", docs_url="/")
app.include_router(router)

async def main():
    await on_startup()
    await on_shutdown()
    
    uvicorn.run("main:app", reload=True)


if __name__ == "__main__":
    asyncio.run(main())