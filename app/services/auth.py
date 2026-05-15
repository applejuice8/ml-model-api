from sqlalchemy.orm import Session
from app.models import User
from app.dependencies import ph


def get_user_by_username(username: str, db: Session) -> User | None:
    return db.query(User).where(User.username == username).first()


def create_user(username: str, password: str, db: Session) -> User:
    user=User(username=username, password=ph.hash(password))
    db.add(user)
    db.commit()
    return user
