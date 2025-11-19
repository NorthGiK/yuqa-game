from aiogram import Router

from src.handlers.telegram.common import router as main_router
from src.handlers.telegram.battle import router as battle_router


router = Router()

router.include_routers(
    main_router,
    battle_router,
)