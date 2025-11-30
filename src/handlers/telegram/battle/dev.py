from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.battles.logic.domain import Battle_T, BattlesManagement
from src.battles.logic.process import start_battle
from src.battles.schemas import SStandardBattleChoice
from src.constants import BattleInProcessOrEnd
from src.users.models import MUser
from src.database.core import AsyncSessionLocal


api_router = APIRouter(prefix="/dev")

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
) -> Optional[bool]:
    return await start_battle(user_id=user_id, type=type)


@api_router.post("/process_battle")
async def handle_user_step(
		choice: SStandardBattleChoice,
	) -> Optional[BattleInProcessOrEnd]:
    battle: Optional[Battle_T] = BattlesManagement.get_battle(choice.battle_id)
    if battle is None:
        return None

    used_bonus: int = sum((choice.hits, choice.blocks, choice.bonus))
    user_action_score: int = battle.get_user(user_id=choice.user_id).action_score #type:ignore

    if used_bonus > user_action_score:
        raise HTTPException(401, "too much used bonus!")
    elif used_bonus < user_action_score:
        raise HTTPException(401, "too few used bonus!")

    return battle.add_step(choice=choice)