# import json
# import os
# # from typing import overload

# from sqlalchemy.ext.asyncio import AsyncSession

# from src.cards.models import MCard
# from src.database.core import get_db


# @overload
# async def create_raw_card(card: int) -> bool:
  # ...

# @overload
# async def create_raw_card(card: MCard) -> bool:
  # ...
  
# async def create_raw_card(card) -> bool:
  # return bool()
  

# async def loads_raw_card() -> None:
#   db: AsyncSession = await get_db()
  
#   cards = []
#   for card in os.listdir("./dir/"):
#     with open(f"./dir/{card}", 'r') as f:
#       raw = f.read()
#       jsoned = json.loads(raw)
#       card = MCard(**jsoned)
#       cards.append(card)
      
#   db.add_all(cards)
#   await db.commit()