from sqlalchemy.orm import Mapped, mapped_column

from src.database.core import Base


class MBattleQueue(Base):
  __tablename__ = 'battle_queues'
  _prim_id: Mapped[int] = mapped_column(primary_key=True)
  
  user_id: Mapped[int] = mapped_column()
  deck: Mapped[str] = mapped_column()