from argon2 import PasswordHasher
from fastapi import HTTPException, status
from sqlalchemy.orm import Session


from app.models.api_key import APIKey

ph = PasswordHasher(time_cost=2, memory_cost=65536, parallelism=2)

async def validate_api_key(api_key: str, db: Session):
    # Check if API key exists
    db_key = db.query(APIKey).where(APIKey.key == api_key).first()
    if not db_key:
        return False
    
    return db_key
