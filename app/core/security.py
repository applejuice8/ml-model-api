from argon2 import PasswordHasher
from fastapi import HTTPException, status
from sqlalchemy.orm import Session


from app.models.api_key import APIKey

ph = PasswordHasher(time_cost=2, memory_cost=65536, parallelism=2)

def validate_api_key(api_key: str, db: Session):
    db_keys = db.query(APIKey).where(APIKey.is_active == True).all()
    for db_key in db_keys:
        try:
            if ph.verify(db_key.key, api_key):
                return db_key
        except Exception:
            continue
    return None
