from sqlalchemy.orm import Session
from app.models import APIKey, Record


def record_api_usage(db_key: APIKey, db: Session) -> Record:
    record = Record(api_key_id=db_key.id)
    db.add(record)
    db.commit()
    return record
