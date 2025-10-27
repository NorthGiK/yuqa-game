from fastapi import APIRouter

from .debug_views import router as v_r


router = APIRouter()

router.include_router(v_r, tags=["view"])