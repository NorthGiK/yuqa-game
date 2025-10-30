import datetime

from sqlalchemy.orm import Mapped, mapped_column

from src.database.BaseModel import Base


def get_time() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)

class MUser(Base):
    __tablename__ = 'users_table'
    # _prim_id: Mapped[int] = mapped_column(primary_key=True)

    id: Mapped[int] = mapped_column(primary_key=True)
    role: Mapped[str] = mapped_column()
    active: Mapped[bool] = mapped_column(default=True)
    create_at: Mapped[datetime.datetime] = mapped_column(default=get_time)