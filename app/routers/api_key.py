from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.auth import AuthRequest
from app.schemas.api_key import APIKeyResponse
from app.dependencies import get_db, ph
from app.services.api_key import get_user_by_username, create_api_key


router = APIRouter(prefix='/api-key', tags=['api_key'])


@router.post('/create', response_model=APIKeyResponse, status_code=status.HTTP_201_CREATED)
async def signup(req: AuthRequest, db: Session = Depends(get_db)):
    # Check if user exists
    user = get_user_by_username(req.username, db)
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail='Username does not exists')
    
    # Check password
    ph.verify(user.password, req.password)

    # Create API key
    raw_key = create_api_key(user, db)

    return APIKeyResponse(key=raw_key)
