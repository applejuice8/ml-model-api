from fastapi import FastAPI
from app.routers import api_key, auth, predict

app = FastAPI()

app.include_router(api_key.router)
app.include_router(auth.router)
app.include_router(predict.router)
