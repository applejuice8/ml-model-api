from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.auth import SignupRequest, LoginRequest, AuthResponse
from app.dependencies import get_db, ph
from app.models import User, APIKey
import secrets

router = APIRouter(prefix='/auth', tags=['auth'])

# hashed = ph.hash("my_password")
# ph.verify(hashed, "my_password")


@router.post('/signup', response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup(req: SignupRequest, db: Session = Depends(get_db)):
    # Check if username taken
    user = db.query(User).where(User.username == req.username)
    if user:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail='Username already exists')
    
    # Create user
    user=User(username=req.username, password=ph.hash(req.password))
    db.add(user)
    db.flush()

    # Create API key
    key = APIKey(key=secrets.token_urlsafe(32), user_id=user.id)
    db.add(key)
    db.commit()

    return AuthResponse(api_key=key)
