from ctypes import Union
import json
from typing import Literal, Optional

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.battles.logic.domain import (
  Battle,
  BattleStandard, 
  BattlesManagement,
)
from src.battles.models import MBattleQueue
from src import constants
from src.battles.schemas import SStandardUserChoice
# from src.schemas import SUserChoice


async def create_queue(user_id: int, db: AsyncSession, deck: list[int]) -> None:
  queue = MBattleQueue(user_id=user_id, deck=json.dumps(deck))
  db.add(queue)
  await db.commit()
  
  
async def init_battle(
  user_id: int, 
  queue: MBattleQueue, 
  db: AsyncSession,
  deck1: Optional[list[int]] = None,
  deck2: Optional[list[int]] = None,
) -> Optional[str]:
    
  battle_id: Optional[str] = await BattlesManagement.create_battle(
    usr1=user_id,
    usr2=queue.user_id,
    deck1=deck1,
    deck2=deck2,
  ) 
  await db.delete(queue)
  await db.commit()
  
  return battle_id


async def start_battle(
  user_id: int,
  db: AsyncSession,
  deck: list[int],
) -> Optional[str]:
  query = select(MBattleQueue)
  queue: Optional[MBattleQueue] = (await db.execute(query)).scalar_one_or_none()
  if queue is None:
    await create_queue(user_id=user_id, db=db, deck=deck)
    return None

  return await init_battle(
    user_id=user_id,
    queue=queue,
    db=db,
    deck1=deck,
    deck2=json.loads(queue.deck),
  )


# async def handle_solo_battle(
#   battle: constants.Battle.SOLO_BATTLE.value,
#   # choice: SUserChoice,
# ) -> types.Local_Battle_State | Literal[constants.BattleState.global_.end]:
#   battle_status = battle.add_step(
#     user_id=choice.user_id,
#     choice=choice,
#   )
#   return battle_status
  
  
async def handle_standard_battle(
  # battle: constants.Battle.SOLO_BATTLE.value,
  battle: BattleStandard,
  choice: SStandardUserChoice,
) -> tuple[constants.BattleState.local, constants.BattleState.global_]:
  battle_status = battle.add_step(
    user_id=choice.user_id,
    choice=choice,
  )
  return battle_status

async def handle_user_step(choice: SStandardUserChoice):
  battle = BattlesManagement.get_battle(choice.battle_id)
  try:
    battle_status = battle.add_step(choice=choice)
  except AttributeError:
    return None
  return battle_status

# async def handle_user_step(choice: SStandardUserChoice):
#   battle: Battle = BattlesManagement.battles[choice.battle_id]
#   if choice.user_id not in (battle.user1, battle.user2):
#     raise HTTPException(
#       status_code=status.HTTP_403_FORBIDDEN,
#       detail="user don't from this battle session!",
#     )

#   type = choice.type
#   if type == constants.BattleSolo:
#     return await handle_solo_battle(battle=battle, choice=choice)
#   elif type == constants.BattleStandard:
#     return await handle_standard_battle(battle=battle, choice=choice)

#   return None