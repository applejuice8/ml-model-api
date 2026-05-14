from app.db.database import Base
from sqlalchemy import DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

class Record(Base):
    __tablename__ = 'record'
    
    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )
    used_at: Mapped[DateTime] = mapped_column(
        DateTime,
        server_default=func.now()
    )
    api_key_id: Mapped[int] = mapped_column(
        ForeignKey('api_key.id')
	)

    api_key: Mapped['APIKey'] = relationship(        # type: ignore
        back_populates='records'
	)