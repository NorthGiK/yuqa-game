from datetime import timedelta
from typing import Annotated, Optional

from sqlalchemy import select

from src.battles.logic.domain import (
    Battle_T,
    BattleStandard,
    BattlesManagement,
)
from src.battles.models import BattleType, MBattleQueue
from src import constants
from src.battles.schemas import SStandardBattleChoice
from src.database.core import AsyncSessionLocal
from src.handlers.rabbit.constants import INIT_BATTLE_QUEUE
from src.logs import dev_configure, get_logger
from src.users.models import MUser
from src.utils.decorators import log_func_call
from src.handlers.rabbit.core import rabbit
from src.utils.redis_cache import redis


log = get_logger(__name__)
dev_configure()


@log_func_call(log)
async def create_queue(
    user_id: int,
    type: Annotated[str, BattleType],
    rating: int,
) -> None:
    queue = MBattleQueue(user_id=user_id, rating=rating, type=type)
    async with AsyncSessionLocal() as session:
        session.add(queue)
        await session.commit()


@log_func_call(log)
async def init_battle(
    user_id: int,
    queue: MBattleQueue,
    type: Annotated[str, BattleType],
) -> None:
    battle_id: Optional[str] = await BattlesManagement.create_battle(
        usr1=user_id,
        usr2=queue.user_id,  # type:ignore
        type=type,
    )
    if battle_id is None:
        raise Exception("Can't create a battle error!")

    async with AsyncSessionLocal() as db:
        await db.delete(queue)
        await db.commit()

    for id in (user_id, queue.user_id):
        await redis.setex(f"battle:{id}", timedelta(minutes=5), battle_id)

    await rabbit.publish(queue=INIT_BATTLE_QUEUE, message=[user_id, queue.user_id])  # type:ignore


@log_func_call(log)
async def start_battle(
    user_id: int,
    type: Annotated[str, Battle_T],
) -> Optional[bool]:
    """
    старт боя: создание очереди на бой, если не нашлось совпаденией,
    иначе создаёт бой в бд и обработчике боев (`BattlesManagement`)

    если создался бой, то через rabbit вызовется бой у пользователся

    :param user_id: телеграм id пользователя
    :type user_id: int
    :param type: тип боя из `BattleType`
    :type type: Annotated[str, Battle_T]

    :return: возвращает `True` если бой начался, `False` если в очереди, `None` если пользователь не найден
    :rtype: bool | None
    """
    user_query = select(MUser).where(MUser.id == user_id)
    async with AsyncSessionLocal() as session:
        user = (await session.execute(user_query)).scalar_one_or_none()
        if user is None:
            return None

    query = select(MBattleQueue).where(MBattleQueue.rating == user.rating)
    async with AsyncSessionLocal() as session:
        queue: Optional[MBattleQueue] = (
            await session.execute(query)
        ).scalar_one_or_none()

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


@log_func_call(log)
async def handle_standard_battle(
    battle: BattleStandard,
    choice: SStandardBattleChoice,
) -> constants.BattleInProcessOrEnd:
    battle_status = battle.add_step(
        choice=choice,
    )
    return battle_status
