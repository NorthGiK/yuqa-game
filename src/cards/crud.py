from dataclasses import asdict
from typing import Any, Iterable, Optional, Sequence

from sqlalchemy import Select, select

from src.cards.models import Card, Deck, MCard, Rarity
from src.database.core import AsyncSessionLocal
from src.users.models import MUser


async def get_card(id: int) -> Optional[MCard]:
    """
    return card by their id
    """
    query = select(MCard).where(MCard.id == id)
    async with AsyncSessionLocal() as db_session:
        card: Optional[MCard] = (await db_session.execute(query)).scalar_one_or_none()

    return card


async def _base_get_cards(query: Select[Any]) -> Sequence[MCard] | None:
    """
    returns cards by their id
    """
    async with AsyncSessionLocal() as session:
        try:
            cards: Sequence[MCard] = (await session.execute(query)).scalars().all()
        except:
            return None

    return cards


async def get_cards(ids: Iterable[int]) -> Optional[Sequence[MCard]]:
    query = select(MCard).where(MCard.id.in_(ids))
    cards: Sequence[MCard] | None = await _base_get_cards(query=query)

    return cards

async def get_deck(user_id: int) -> Optional[Deck]:
    user_inventory_query = select(MUser.deck).where(MUser.id == user_id)
    async with AsyncSessionLocal() as session:
        inventory = (await session.execute(user_inventory_query)).scalar_one_or_none()

    deck_query = select(MCard).where(MCard.id.in_(inventory))
    async with AsyncSessionLocal() as session:
        cards = (await session.execute(deck_query)).scalars().all()

    return Deck(id=user_id, cards=[Card(
        id=card.id,
        name=card.name,
        universe=card.universe,
        rarity=card.rarity,
        atk=card.atk,
        hp=card.hp,
        def_=card.def_,
    ) for card in cards])


async def get_cards_by_rarity(
    user_id: int,
    rarity: Rarity,
) -> list[MCard]:
    inventory_query = (
        select(MUser.inventory)
        .where(
            MUser.id == user_id,
        )
        .distinct()
    )
    async with AsyncSessionLocal() as session:
        card_ids: list[int] = (await session.execute(inventory_query)).scalar_one()

    card_ids_query = (
        select(MCard)
        .where(
            MCard.rarity == rarity.name,
            MCard.id.in_(
                card_ids,
            )
        ).distinct()
    )
    async with AsyncSessionLocal() as session:
        cards = (await session.execute(card_ids_query)).scalars().all()

    return cards