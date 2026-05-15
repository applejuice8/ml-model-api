# Health

curl http://127.0.0.1:8000/health

# Signup

curl -X POST http://127.0.0.1:8000/auth/signup -H "Content-Type: application/json" -d '{"username": "abc123", "password": "abc123"}'

# Generate API Key

curl -X POST http://127.0.0.1:8000/api-key/create -H "Content-Type: application/json" -d '{"username": "abc123", "password": "abc123"}'

# Sample API Key

TE2bn0hqqMtudQ7TAXQ_Q14_l0iAVdNWFo6DHSYx5qk

# Test Predict

curl -X POST http://127.0.0.1:8000/predict/v1 -H "Content-Type: application/json" -H "X-API-KEY: TE2bn0hqqMtudQ7TAXQ_Q14_l0iAVdNWFo6DHSYx5qk" -d '{"X-data": [1, 2, 3]}'
