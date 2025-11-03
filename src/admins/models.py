from sqlalchemy.orm import Mapped, mapped_column

from src.database.BaseModel import Base


class MRoles(Base):
    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(primary_key=True)
    privilegies: Mapped[dict[str, int]] = mapped_column(nullable=False)