# Health

curl http://127.0.0.1:8000/health

# Signup

curl -X POST http://127.0.0.1:8000/auth/signup -H "Content-Type: application/json" -d '{"username": "abc123", "password": "abc123"}'

# Generate API Key

curl -X POST http://127.0.0.1:8000/api-key/create -H "Content-Type: application/json" -d '{"username": "abc123", "password": "abc123"}'

# Sample API Key

TE2bn0hqqMtudQ7TAXQ_Q14_l0iAVdNWFo6DHSYx5qk

# Sample Spam

SIX chances to win CASH! From 100 to 20,000 pounds txt> CSH11 and send to 87575. Cost 150p/day, 6days, 16+ TsandCs apply Reply HL 4 info

# Test Spam

curl -X POST http://127.0.0.1:8000/predict -H "Content-Type: application/json" -H "X-API-KEY: TE2bn0hqqMtudQ7TAXQ_Q14_l0iAVdNWFo6DHSYx5qk" -d '{"X-data": ["SIX chances to win CASH! From 100 to 20,000 pounds txt> CSH11 and send to 87575. Cost 150p/day, 6days, 16+ TsandCs apply Reply HL 4 info"]}'

# Test Ham

curl -X POST http://127.0.0.1:8000/predict -H "Content-Type: application/json" -H "X-API-KEY: TE2bn0hqqMtudQ7TAXQ_Q14_l0iAVdNWFo6DHSYx5qk" -d '{"X-data": ["Go until jurong point, crazy.. Available only in bugis n great world la e buffet... Cine there got amore wat..."]}'
