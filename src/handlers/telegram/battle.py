from datetime import datetime
from aiogram import F, Router
from aiogram.types import CallbackQuery
from fastapi import APIRouter
from pydantic import BaseModel

from src.battles.logic.process import start_battle
from src.cards.crud import get_deck
from src.cards.models import Deck
from src.database.core import AsyncSessionLocal
from src.handlers.telegram.constants import Navigation
from src.users.models import MUser


router = Router()
api_router = APIRouter()

class User(BaseModel):
    rating: int
    inventory: list[int]
    deck: list[int]
    active: bool
    created_at: datetime

@api_router.post("/create_user")
async def create_user_handler(data: User):
    user = MUser(**data.model_dump())
    async with AsyncSessionLocal() as session:
        session.add(user)
        await session.commit()
    
    return "OK"

@api_router.post("/start_battle")
async def start_duo_battle_api(
    user_id: int,
    type: str,
    deck: Deck,
):
    return await start_battle(user_id=user_id, type=type, deck=deck)

@router.callback_query(F.data == Navigation.in_battle.duo)
async def start_duo_battle(clbk: CallbackQuery) -> None:
    user_id: int = clbk.from_user.id
    deck = await get_deck(user_id=user_id)
    if deck is None:
        clbk.answer(f"nihua ne work")
        return

    await clbk.answer("goog")
    await start_battle(clbk.from_user.id, deck=deck, type="duo")
