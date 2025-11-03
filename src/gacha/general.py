from dataclasses import dataclass
from fractions import Fraction
import random

from sqlalchemy import func, select

from src.cards import models as card_models
from src.cards.models import MCard, MUniverse
from src.database.core import AsyncSessionLocal
from src.gacha.exceptions import NotSameLengthOfRaritiesAndCanches, NotSelectedCardError


@dataclass(slots=True)
class RandomManager:
    rarities: list[card_models.Rarity]
    chanches: list[Fraction]

    def __post_init__(self) -> None:
        if len(self.rarities) != len(self.rarities):
            raise NotSameLengthOfRaritiesAndCanches()
    

    def update_self(
        self,
        rarities_canches: dict[card_models.Rarity, Fraction],
    ) -> None:
        self.rarities, self.chanches = list(rarities_canches.keys()), list(rarities_canches.values())


    def choose_rarity(self) -> card_models.Rarity:
        return random.choices(self.rarities, weights=self.chanches, k=1)[0]


    async def choose_card(
        self,
        rarity: card_models.Rarity,
        universe: MUniverse,
    ) -> int:
        async with AsyncSessionLocal() as session:
            query = select(MCard.id) \
                    .where(MCard.rarity == rarity, MCard.universe == universe) \
                    .order_by(func.random()) \
                    .fetch(1)

            card_id = (await session.execute(query)).scalar_one_or_none()
            if card_id is None:
                raise NotSelectedCardError()

            return card_id
