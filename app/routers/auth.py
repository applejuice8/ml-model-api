from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.auth import AuthRequest, AuthResponse
from app.dependencies import get_db
from app.services.auth import get_user_by_username, create_user

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/signup', response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup(req: AuthRequest, db: Session = Depends(get_db)):
    # Check if username taken
    if get_user_by_username(req.username, db):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail='Username already exists')

    # Create user
    user = create_user(req.username, req.password, db)

    return AuthResponse(status='success')
