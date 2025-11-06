from typing import Any, Iterable, Optional, Sequence

from sqlalchemy import Select, select
from sqlalchemy.sql import operators
from sqlalchemy.ext.asyncio import AsyncSession

from src.cards.models import Card, CardInInventory, MCard, Rarity
from src.database.core import AsyncSessionLocal, get_db
from src.shared.redis_broker import redis
from src.users.models import MUser


async def get_card(id: int) -> Optional[Card]:
    db_session: AsyncSession = await get_db()
    query = select(MCard).where(MCard.id == id)
    card: Optional[MCard] = (
        await db_session.execute(query)
    ).scalar_one_or_none()

    if card is None:
        return None

    args = card.__table__.columns
    return Card.model_validate(args, from_attributes=True)


async def _base_get_cards(query: Select[Any]) -> Sequence[MCard] | None:
    """
    returns cards by their id
    """
    async with AsyncSessionLocal() as session:
        try:
            cards: Sequence[MCard] = (
                await session.execute(query)
            ).scalars().all()
        except:
            return None

    return cards

async def get_cards(ids: Iterable[int]) -> list[Card] | None:
    query = select(MCard).where(MCard.id.in_(ids))
    raw_cards: Sequence[MCard] | None = await _base_get_cards(query=query)
    if raw_cards is None:
        return None

    cards: list[Card] = [Card.model_validate(card, from_attributes=True) for card in raw_cards]
    return cards

async def get_cards_by_rarity(
    user_id: int,
    rarity: Rarity,
    next: bool,
) -> Optional[list[CardInInventory]]:
    card_id_in: Optional[int] = await redis.get(f"inventory_page:{user_id}")
    if card_id_in is None:
        return None

    card_ids_query = (
        select(
            MCard.id, 
            MCard.name, 
            MCard.atk, 
            MCard.hp,
        ).where(
            MCard.rarity == rarity,
            MCard.id.in_(
                select(MUser.inventory)
                .where(
                    MUser.id == user_id,
                    MUser.inventory.any(card_id_in, #type:ignore
                                        operator=operators.gt if next
                                        else operators.lt)) 
                .limit(10)
            )
        )
    )

    async with AsyncSessionLocal() as session:
        cards: Sequence[tuple[int, str, int, int]] = (await session.execute(card_ids_query)).scalars().all()

    parsed_cards: list[CardInInventory] = [
        CardInInventory(
            id=card[0],
            name=card[1],
            atk=card[2],
            hp=card[3],
        )
        for card in cards
    ]
    return parsed_cards


async def get_decks(
        ids: dict[int, Iterable[int]],
    ) -> dict[int, list[Card]] | None:
    # TODO: Что-нибудь придумать, чтобы не делать 2 запроса в бд

    decks: dict[int, list[Card]] = {}

    for user_id, card_ids in ids.items():
        cards = await get_cards(card_ids)
        if cards is None:
            return None

        decks[user_id] = cards

    return decks
