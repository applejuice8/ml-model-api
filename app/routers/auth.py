from fastapi import APIRouter

router = APIRouter(prefix='/auth', tags=['auth'])

@router.post('/signup')
async def signup():
    pass