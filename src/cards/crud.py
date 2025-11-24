from typing import Any, Iterable, Optional

from sqlalchemy import Select, select

from src.battles.logic.common import CommonCardInBattle
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


async def _base_get_cards(query: Select[Any]) -> Optional[list[MCard]]:
    """
    returns cards by their id
    """
    async with AsyncSessionLocal() as session:
        try:
            cards: list[MCard] = (await session.execute(query)).scalars().all()
        except:
            return None

    return cards


async def get_cards(ids: Iterable[int]) -> Optional[list[CommonCardInBattle]]:
    query = select(MCard).where(MCard.id.in_(ids))
    cards: list[MCard] | None = await _base_get_cards(query=query)
    if cards is None:
        return None

    return await CommonCardInBattle.from_model(cards)


async def get_cards_by_user_id(id: int) -> Optional[list[CommonCardInBattle]]:
    query = select(MUser.deck).where(MUser.id == id)
    async with AsyncSessionLocal() as session:
        raw_deck: Optional[list[int]] = (await session.execute(query)).scalar_one_or_none()

    return await get_cards(raw_deck) #type:ignore


async def get_deck(user_id: int) -> Optional[Deck]:
    user_inventory_query = select(MUser.deck).where(MUser.id == user_id)
    async with AsyncSessionLocal() as session:
        inventory = (await session.execute(user_inventory_query)).scalar_one_or_none()

    if inventory is None:
        return None

    deck_query = select(MCard).where(MCard.id.in_(inventory))
    async with AsyncSessionLocal() as session:
        cards = (await session.execute(deck_query)).scalars().all()
    
    if not all(cards):
        return None

    return Deck(id=user_id, cards=[Card(
        id=card.id, #type:ignore
        name=card.name, #type:ignore
        universe=card.universe, #type:ignore
        rarity=card.rarity, #type:ignore
        atk=card.atk, #type:ignore
        hp=card.hp, #type:ignore
        def_=card.def_, #type:ignore
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