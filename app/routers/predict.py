from fastapi import APIRouter, status, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.schemas.predict import PredictRequest, PredictResponse
from app.dependencies import get_db, validate_api_key
from app.models import Record


router = APIRouter(prefix='/predict', tags=['predict'])

@router.post('/v1', response_model=PredictResponse)
async def predict(
    req: PredictRequest,
    api_key: str = Header(..., alias='X-API-KEY'),
    db: Session = Depends(get_db)
):
    # Validate API key
    db_key = validate_api_key(api_key, db)
    if not db_key:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail='Invalid API key')

    # Add usage record
    record = Record(api_key_id=db_key.id)
    db.add(record)
    db.commit()

    return PredictResponse(prediction=[1, 2, 3])
