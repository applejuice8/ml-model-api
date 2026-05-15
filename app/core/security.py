from argon2 import PasswordHasher
from fastapi import Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from argon2.exceptions import VerifyMismatchError
from app.dependencies import get_db

from app.models.api_key import APIKey

ph = PasswordHasher(time_cost=2, memory_cost=65536, parallelism=2)

def validate_api_key(
    api_key: str = Header(..., alias='X-API-KEY'),
    db: Session = Depends(get_db)
) -> APIKey:
    db_keys = db.query(APIKey).where(
        APIKey.prefix == api_key[:8],
        APIKey.is_active == True
    ).all()

    for db_key in db_keys:
        try:
            ph.verify(db_key.key, api_key)
            return db_key
        except VerifyMismatchError:
            continue
    raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail='Invalid API key')
