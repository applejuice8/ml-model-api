from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.predict import PredictRequest, PredictResponse
from app.dependencies import get_db, validate_api_key
from app.models import Record, APIKey
from app.services.predict import record_api_usage


router = APIRouter(prefix='/predict', tags=['predict'])

@router.post('/v1', response_model=PredictResponse)
async def predict(
    req: PredictRequest,
    db_key: APIKey = Depends(validate_api_key),
    db: Session = Depends(get_db)
):
    record = record_api_usage(db_key, db)

    return PredictResponse(prediction=[1, 2, 3])
