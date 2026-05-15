from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.predict import PredictRequest, PredictResponse
from app.dependencies import get_db, validate_api_key
from app.models import APIKey
from app.services.predict import record_api_usage


router = APIRouter(tags=['predict'])

@router.post('/predict', response_model=PredictResponse)
async def predict(
    req: PredictRequest,
    db_key: APIKey = Depends(validate_api_key),
    db: Session = Depends(get_db)
):
    record = record_api_usage(db_key, db)
    prediction = list(map(lambda x: x**2, req.X_data))

    return PredictResponse(prediction=prediction)
