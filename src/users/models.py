from dataclasses import dataclass
import datetime

from src.database.BaseModel import Base


@dataclass(slots=True)
class MUser(Base):
    id: int

    rating: int
    cards: list[int]
    inventory: list[int]

    active: bool
    create_at: datetime.date


CREATE_USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users_t (
    id INT PRIMARY KEY,

    rating INT,
    cards INT ARRAY,
    inventory INT ARRAY,

    active BOOl,
    created_at DATE
);
"""