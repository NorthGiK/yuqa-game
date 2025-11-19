from fastapi import APIRouter

from src.handlers.telegram.battle import api_router


router = APIRouter()

router.include_router(api_router, tags=["view"])