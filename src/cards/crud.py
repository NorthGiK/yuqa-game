from typing import Iterable, Optional

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.cards import models
from src.database.core import get_db


async def get_card(id: int) -> Optional[models.Card]:
    db_session: AsyncSession = await get_db()
    query = select(models.MCard).where(models.MCard._prim_id == id)
    card: Optional[models.MCard] = (
        await db_session.execute(query)
    ).scalar_one_or_none()
    if card is None:
        return None

    return models.Card(
        id=card._prim_id,
        name=card.name,
        universe=card.universe,
        rarity=card.rarity,
        description=card.description,
        class_=card.class_,
        def_=card.def_,
        atk=card.atk,
        hp=card.hp,
    )


async def get_cards(ids: Iterable[int]) -> list[models.Card]:
    """
    returns cards by their id
    """
    cards: list[models.Card] = []
    for id in ids:
        card = await get_card(id)
        if card is None:
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="invalid card id!",
            )
        cards.append(card)

    return cards


async def get_decks(
        ids: dict[int, Iterable[int]],
    ) -> dict[int, list[models.Card]]:
    decks: dict[int, list[models.Card]] = {}
    for user, cards in ids.items():
        decks[user] = await get_cards(cards)

    return decks
