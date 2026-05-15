from app.db.database import Base
from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )
    username: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        unique=True
    )
    password: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    created_at: Mapped[DateTime] = mapped_column(
        DateTime,
        server_default=func.now()
    )

    api_keys: Mapped[list['APIKey']] = relationship(    # type: ignore
        back_populates='user'
    )
