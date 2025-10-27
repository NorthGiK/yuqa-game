from typing import Annotated, Optional, Sequence
import json
import os
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from src.battles.logic.domain import BattleWithDeck, BattlesManagement
from src.battles.logic.process import start_battle
from src.cards.models import MAbility, MCard
from src.database.core import DBSession
from src.battles.schemas import SStandardBattleChoice


router = APIRouter()


@router.post("/load_cards")
async def load(db_session: DBSession):
    cards = abilities = []
    for card, ability in zip(os.listdir("./dir/"), os.listdir("./fold/")):
        with open(f"./dir/{card}", "r") as f:
            raw = f.read()
            jsoned = json.loads(raw)
            card = MCard(**jsoned)
            del jsoned
            cards.append(card)

        with open(f"./dir/{ability}", "r") as f:
            raw = f.read()
            jsoned = json.loads(raw)
            ability = MAbility(**jsoned)
            abilities.append(ability)

    cards += abilities
    db_session.add_all(cards)
    await db_session.commit()


@router.get("/cards")
async def view_cards(db_session: DBSession):
    query = select(MCard)
    cards: Optional[Sequence[MCard]] = (await db_session.execute(query)).scalars().all()

    return {"ok": True, "cards": cards}


@router.post("/start_battle")
async def start_battle_handler(user_id: int, deck: list[int], db_session: DBSession):
    if res := await start_battle(
        user_id=user_id,
        deck=deck,
        db=db_session,
    ):
        return res
    return None


@router.post("/std_battle")
async def process_std_battle(choice: SStandardBattleChoice):
    battle: BattleWithDeck = BattlesManagement.get_battle(choice.battle_id)
    if battle is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="bebebe",
        )

    battle.add_step(choice=choice)
    return {"curr": repr(battle)}


@router.get("/view_battle")
async def view_battle_handler(id: Annotated[str, UUID]):
    battle = BattlesManagement.get_battle(id)
    return {"battle": repr(battle)}
