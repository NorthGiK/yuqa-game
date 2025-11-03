from sqlalchemy import text


class MBattleQueue:
  id: int
  user_id: int
  deck: list[int]


CREATE_BATTLE_QUEUE_TABLE = text("""
CREATE TABLE IF NOT EXISTS battle_queues (
  id INT PRIMARY KEY,
  user_id INT,
  deck INT ARRAY
);
""")