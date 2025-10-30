from aiogram import Router

from src.handlers.telegram.common import router as main_router


router = Router()

router.include_routers(
    main_router,
)