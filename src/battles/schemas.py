from pydantic import BaseModel

from src import constants


class SBaseChoice(BaseModel):
    user_id: int
    battle_id: str

    hits: int
    blocks: int
    bonus: int


class SStandardBattleChoice(SBaseChoice):
    target: int
    selected_card: int


class SSoloBattleChoice(SBaseChoice):
  ...


class SCard(BaseModel):
    hp: int
    atk: int
    pos: int
    def_: int
    class_: constants.Card.class_
    rarity: constants.Card.rarity
