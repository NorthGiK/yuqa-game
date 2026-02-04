from dataclasses import dataclass, field
from fractions import Fraction
import random
from typing import Annotated, Optional

from sqlalchemy import func, select

from src.cards.models import MCard, Rarity
from src.database.core import AsyncSessionLocal
from src.gacha.exceptions import NotSameLengthOfRaritiesAndCanches, NotSelectedCardError
from src.utils.patterns import Singletone


@dataclass(frozen=True, slots=True, eq=False)
class RandomManager(Singletone):
    _rarities: list[Rarity] = field(default_factory=lambda: [r for r in Rarity])
    _chanches: list[Fraction] = field(
        default_factory=lambda: [
            # Fraction(90, 100),              # 90 / 100
            # Fraction(Fraction(15, 2), 100), # 7.5 / 100
            # Fraction(Fraction(5, 2), 100),  # 2.5 / 100
            50,
            35,
            15,
        ]
    )

    def __post_init__(self) -> None:
        self.validate_chances()

    def validate_chances(self) -> None:
        if len(self._rarities) != len(self._rarities):
            raise NotSameLengthOfRaritiesAndCanches()

    def choose_rarity(self) -> Rarity:
        return random.choices(self._rarities, weights=self._chanches, k=1)[0]

    @classmethod
    async def choose_card(
        cls,
        rarity: Rarity | Annotated[str, Rarity],
        universe: Optional[str] = None,
    ) -> MCard:
        async with AsyncSessionLocal() as session:
            query = select(MCard).where(MCard.rarity == rarity)
            if universe is not None:
                query = query.where(MCard.universe == universe)

            query = query.order_by(func.random()).limit(1)

            card = (await session.execute(query)).scalar_one_or_none()
            if card is None:
                raise NotSelectedCardError()

        return card
