from sqlalchemy.orm import Session
from app.models import User, APIKey
from app.dependencies import ph
import secrets


def get_user_by_username(username: str, db: Session) -> User | None:
    return db.query(User).where(User.username == username).first()


def create_api_key(user: User, db: Session) -> str:
    raw_key = secrets.token_urlsafe(32)
    key = APIKey(
        key=ph.hash(raw_key),
        prefix=raw_key[:8],
        user_id=user.id
    )
    db.add(key)
    db.commit()
    return raw_key
