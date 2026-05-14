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
    key = APIKey(key=secrets.token_urlsafe(32), user_id=user.id)
    db.add(ph.hash(key))
    db.commit()

    return APIKeyResponse(api_key=key)
