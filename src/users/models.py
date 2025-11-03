from dataclasses import dataclass
import datetime

from sqlalchemy import text


@dataclass(slots=True)
class MUser:
    id: int

    rating: int
    cards: list[int]
    inventory: list[int]

    active: bool
    create_at: datetime.date


CREATE_USERS_TABLE = text("""
CREATE TABLE IF NOT EXISTS users_t (
    id INT PRIMARY KEY,

    rating INT,
    cards INT ARRAY,
    inventory INT ARRAY,

    active BOOl,
    created_at DATE
);
""")