from typing import Annotated, Optional

from sqlalchemy import select

from src.battles.logic.common import CommonCardInBattle
from src.battles.logic.domain import (
  Battle_T,
  BattleStandard, 
  BattlesManagement,
)
from src.battles.models import BattleType, MBattleQueue
from src import constants
from src.battles.schemas import SStandardBattleChoice
from src.cards.models import Deck, MCard
from src.database.core import AsyncSessionLocal
from src.users.models import MUser


async def create_queue(
	user_id: int,
	type: Annotated[str, BattleType],
	rating: int,
) -> None:
	queue = MBattleQueue(user_id=user_id, rating=rating, type=type)
	async with AsyncSessionLocal() as session:
		session.add(queue)
		await session.commit()


async def init_battle(
    user_id: int, 
    queue: MBattleQueue, 
	type: Annotated[str, BattleType],
) -> Optional[str]:

	battle_id: Optional[str] = await BattlesManagement.create_battle(
		usr1=user_id,
		usr2=queue.user_id, #type:ignore
		type=type,
	)

	async with AsyncSessionLocal() as db:
		await db.delete(queue)
		await db.commit()

	return battle_id


async def start_battle(
  	user_id: int,
	type: Annotated[str, Battle_T],
) -> Optional[str]:
	user_query = select(MUser).where(MUser.id == user_id)
	async with AsyncSessionLocal() as session:
		user = (await session.execute(user_query)).scalar_one_or_none()
		if user is None:
			return None

	query = select(MBattleQueue).where(MBattleQueue.rating == user.rating)
	async with AsyncSessionLocal() as session:
		queue: Optional[MBattleQueue] = (await session.execute(query)).scalar_one_or_none()

	if queue is None:
		await create_queue(
			user_id=user_id,
			rating=user.rating,
			type=type,
		)
		return None

	return await init_battle(
    	user_id=user_id,
    	queue=queue,
		type=type,
  	)


async def handle_standard_battle(
  	battle: BattleStandard,
  	choice: SStandardBattleChoice,
) -> constants.BattleInProcessOrEnd:
	battle_status = battle.add_step(
		choice=choice,
	)
	return battle_status

async def handle_user_step(choice: SStandardBattleChoice):
  battle = BattlesManagement.get_battle(choice.battle_id)
  try:
    return battle.add_step(choice=choice)
  except AttributeError:
    return None
