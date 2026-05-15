# Health

curl http://127.0.0.1:8000/health

# Signup

curl -X POST http://127.0.0.1:8000/auth/signup -H "Content-Type: application/json" -d '{"username": "abc123", "password": "abc123"}'

# Generate API Key

curl -X POST http://127.0.0.1:8000/api-key/create -H "Content-Type: application/json" -d '{"username": "abc123", "password": "abc123"}'

# Sample API Key

o0FmJXG3h2zzDdWkno2Byk0gQUM8YuBqDvaA5Nn_et8

# Test Predict

curl -X POST http://127.0.0.1:8000/predict/v1 -H "Content-Type: application/json" -H "X-API-KEY: o0FmJXG3h2zzDdWkno2Byk0gQUM8YuBqDvaA5Nn_et8" -d '{"X-data": [1, 2, 3]}'


X-API-KEY
