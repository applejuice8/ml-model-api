from fastapi import APIRouter

router = APIRouter(prefix='/model', tags=['predict'])

@router.post('/predict')
async def predict():
    pass