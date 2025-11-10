import json
import os

from src.cards.models import MAbilities, MCard
from src.database.core import AsyncSessionLocal


async def _create_raw_cards() -> None:
	for filename in os.listdir("./dir"):
		with open(f"./dir/{filename}") as card:
			new_card = MCard(**json.loads(card.read()))

		with open(F"./fold/{filename}") as ability:
			new_ability = MAbilities(**json.loads(ability.read()))

		async with AsyncSessionLocal() as session:
			session.add_all((new_ability, new_card))
			await session.commit()