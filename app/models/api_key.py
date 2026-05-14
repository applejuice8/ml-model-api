from app.db.database import Base
from sqlalchemy import String, DateTime, func, Boolean, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from typing import Literal

class APIKey(Base):
    __tablename__ = 'api_key'
    
    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )
    key: Mapped[int] = mapped_column(
        String(100),
        nullable=False,
        unique=True
    )
    role: Mapped[str] = mapped_column(
        Literal('user', 'admin'),
        default='user'
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )
    created_at: Mapped[DateTime] = mapped_column(
        DateTime,
        server_default=func.now()
    )

    user: Mapped[str] = mapped_column(
        ForeignKey('user.id')
    )