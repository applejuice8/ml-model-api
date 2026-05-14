from app.db.database import Base
from sqlalchemy import String, DateTime, func, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
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
    role: Mapped[Literal['user', 'admin']] = mapped_column(
        String,
        default='user'
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )
    created_at: Mapped[DateTime] = mapped_column(
        DateTime,
        server_default=func.now()
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey('user.id')
	)

    user: Mapped['User'] = relationship(        # type: ignore
        back_populates='api_keys'
	)