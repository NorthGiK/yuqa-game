from dataclasses import asdict
from aiogram import F, Router
from aiogram.types import CallbackQuery
from datetime import datetime
from fastapi import APIRouter, HTTPException

from typing import Optional
from pydantic import BaseModel

from src.battles.logic.domain import BattlesManagement
from src.battles.logic.process import start_battle
from src.battles.models import BattleType
from src.battles.schemas import SStandardBattleChoice
from src.cards.crud import get_deck
from src.constants import BattleInProcessOrEnd
from src.database.core import AsyncSessionLocal
from src.handlers.telegram.constants import Navigation
from src.logs import get_logger, dev_configure
from src.users.models import MUser


router = Router()
api_router = APIRouter()

log = get_logger(__name__)
dev_configure()

@api_router.get("/battles")
async def get_all_battles_handler():
    return {id: asdict(data, dict_factory=lambda: ...) for id, data in BattlesManagement.battles.items()} #type:ignore


class User(BaseModel):
    rating: int
    inventory: list[int]
    deck: list[int]
    created_at: datetime
    active: bool = True


@api_router.post("/create_user")
async def create_user_handler(data: User):
    if data.inventory == [0]:
        data.inventory = [1, 2]
    if data.deck == [0]:
        data.deck = [1,2]

    user = MUser(**data.model_dump())
    async with AsyncSessionLocal() as session:
        session.add(user)
        await session.commit()

    return "OK"


@api_router.post("/start_battle")
async def start_duo_battle_api(
    user_id: int,
    type: str,
) -> Optional[str]:
    return await start_battle(user_id=user_id, type=type)


@api_router.post("/process_battle")
async def handle_user_step(
		choice: SStandardBattleChoice,
	) -> Optional[BattleInProcessOrEnd]:
    battle = BattlesManagement.get_battle(choice.battle_id)
    if battle is None:
        return None

    used_bonus: int = sum((choice.hits, choice.blocks, choice.bonus))
    user_action_score: int = battle.get_user(choice.user_id).action_score #type:ignore

    if used_bonus > user_action_score:
        raise HTTPException(401, "too much used bonus!")
    elif used_bonus < user_action_score:
        raise HTTPException(401, "to few used bonus!")

    return battle.add_step(choice=choice)


@router.callback_query(F.data == Navigation.in_battle.duo)
async def start_duo_battle(clbk: CallbackQuery) -> None:
    user_id: int = clbk.from_user.id
    deck = await get_deck(user_id=user_id)
    if deck is None:
        clbk.answer(f"ne work")
        return

    await clbk.answer("goog")
    await start_battle(clbk.from_user.id, type=BattleType.duo)
