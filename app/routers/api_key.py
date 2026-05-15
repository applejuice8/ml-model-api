from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.auth import AuthRequest
from app.schemas.api_key import APIKeyResponse
from app.dependencies import get_db, ph
from app.models import User, APIKey
import secrets

router = APIRouter(prefix='/api-key', tags=['api_key'])


@router.post('/create', response_model=APIKeyResponse, status_code=status.HTTP_201_CREATED)
async def signup(req: AuthRequest, db: Session = Depends(get_db)):
    # Check if user exists
    user = db.query(User).where(User.username == req.username).first()
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail='Username does not exists')
    
    # Check password
    ph.verify(user.password, req.password)

    # Create API key
    raw_key = secrets.token_urlsafe(32)
    key = APIKey(
        key=ph.hash(raw_key),
        prefix=raw_key[:8],
        user_id=user.id
    )
    db.add(key)
    db.commit()

    return APIKeyResponse(key=raw_key)
