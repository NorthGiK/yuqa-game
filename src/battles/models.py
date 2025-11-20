from dataclasses import dataclass
from sqlalchemy import Column, Integer, String

from src.database.BaseModel import Base


class MBattleQueue(Base):
    __tablename__ = "battle_queues"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    rating = Column(Integer, nullable=False)
    type = Column(String, nullable=False)


@dataclass(slots=True, frozen=True)
class BattleType:
    duo = "duo"
    standard = "standard"