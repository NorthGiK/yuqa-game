import json
import os
from typing import Any

from src.cards.models import MCard


def get_card(id: int) -> bool:
  return f"{id}.json" in os.listdir("./raw_cards")

# def create_card(card: MCard) -> bool:
#   if get_card(card._prim_id):
#     return False

#   parsed_data: dict[str, Any] = {}
  
#   return False