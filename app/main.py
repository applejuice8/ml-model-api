from fastapi import FastAPI
from app.routers import api_key, auth, predict

app = FastAPI()

app.include_router(api_key.router)
app.include_router(auth.router)
app.include_router(predict.router)

@app.get('/health')
async def health():
    return {'status': 'ok'}

'''
curl -X POST http://localhost:8000/checkout \
    -H "Content-Type: application/json" \
    -d '{
        "item": {"name":"apple","price":1.5},
        "user": {"name":"Alice","email":"a@b.com"}
    }'
'''
