from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.auth import AuthRequest, AuthResponse
from app.dependencies import get_db, ph
from app.models import User, APIKey
import secrets

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/signup', response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup(req: AuthRequest, db: Session = Depends(get_db)):
    # Check if username taken
    user = db.query(User).where(User.username == req.username)
    if user:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail='Username already exists')

    # Create user
    user=User(username=req.username, password=ph.hash(req.password))
    db.add(user)
    db.commit()

    return AuthResponse(status='success')
