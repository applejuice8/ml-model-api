from fastapi import APIRouter, status, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.schemas.predict import PredictRequest, PredictResponse
from app.dependencies import get_db, validate_api_key


router = APIRouter(prefix='/predict', tags=['predict'])

@router.post('/predict', response_model=PredictResponse)
async def predict(
    req: PredictRequest,
    api_key: str = Header(..., alias='X-API-KEY'),
    db: Session = Depends(get_db)
):
    user_id = validate_api_key(api_key, db)
    if not user_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail='API key does not exists')

    return PredictResponse([1, 2, 3])
