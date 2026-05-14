from app.db.database import Base, engine
from app.models import api_key, user

if __name__ == '__main__':
    Base.metadata.create_all(bind=engine)
