# ML Model API

A REST API for SMS spam detection built with FastAPI. It wraps a scikit-learn MLP classifier trained on the [UCI SMS Spam Collection dataset](https://www.kaggle.com/datasets/uciml/sms-spam-collection-dataset) and gates inference behind API key authentication.

---

## Features

- User registration and account management
- Secure API key issuance using Argon2id hashing with prefix lookup
- SMS spam/ham classification via a TF-IDF + MLP pipeline
- Per-request usage tracking recorded to a SQLite database
- Health check endpoint

---

## Tech Stack

| Layer | Technology |
|---|---|
| Web framework | FastAPI |
| Database ORM | SQLAlchemy |
| Database | SQLite |
| Password / key hashing | Argon2 (`argon2-cffi`) |
| ML model | scikit-learn (`MLPClassifier`) |
| Dataset access | `kagglehub` |
| Model serialization | `joblib` |

---

## Project Structure

```
.
├── app/
│   ├── core/
│   │   ├── config.py          # Settings loaded from .env
│   │   └── security.py        # Argon2 hasher, API key validator
│   ├── db/
│   │   └── database.py        # SQLAlchemy engine and session
│   ├── models/
│   │   ├── user.py            # User ORM model
│   │   ├── api_key.py         # APIKey ORM model
│   │   └── record.py          # Usage record ORM model
│   ├── routers/
│   │   ├── auth.py            # POST /auth/signup
│   │   ├── api_key.py         # POST /api-key/create
│   │   └── predict.py         # POST /predict
│   ├── schemas/               # Pydantic request/response models
│   ├── services/              # Business logic layer
│   ├── dependencies.py        # Shared FastAPI dependencies
│   └── main.py                # App entrypoint, router registration
├── ml/
│   ├── train.py               # Model training script
│   ├── test.py                # Model evaluation script
│   ├── models/
│   │   └── spam_detector.pkl  # Trained pipeline (TF-IDF + MLP)
│   └── test_data/
│       └── spam_data.pkl      # Held-out test set
├── init_db.py                 # Creates database tables
├── requirements.txt
└── .env                       # Environment variables (not committed)
```

---

## Setup

### 1. Clone and install dependencies

```bash
git clone <repo-url>
cd ML_Model_API
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment

Create a `.env` file in the project root:

```env
DATABASE_URI=sqlite:///./database.db
DEBUG=false
```

### 3. Initialize the database

```bash
python init_db.py
```

### 4. Train the ML model (optional — a pre-trained model is included)

Requires a Kaggle account and `kaggle.json` credentials configured.

```bash
python -m ml.train
```

### 5. Start the server

```bash
fastapi dev app/main.py      # development
fastapi run app/main.py      # production
```

---

## API Reference

### `GET /health`

Returns server status.

```bash
curl http://127.0.0.1:8000/health
```

**Response**
```json
{"status": "ok"}
```

---

### `POST /auth/signup`

Creates a new user account.

```bash
curl -X POST http://127.0.0.1:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "secret"}'
```

| Field | Type | Constraints |
|---|---|---|
| `username` | string | 3–20 characters, unique |
| `password` | string | 3–20 characters |

**Response**
```json
{"status": "success"}
```

---

### `POST /api-key/create`

Issues a new API key for an existing user. Store the returned key — it cannot be retrieved again.

```bash
curl -X POST http://127.0.0.1:8000/api-key/create \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "secret"}'
```

**Response**
```json
{"key": "TE2bn0hqqMtudQ7TAXQ_Q14_l0iAVdNWFo6DHSYx5qk"}
```

---

### `POST /predict`

Classifies one or more SMS messages as spam (`1`) or ham (`0`). Requires a valid API key in the `X-API-KEY` header.

```bash
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: <your-api-key>" \
  -d '{"X-data": ["Congratulations! You have won a free prize. Call now."]}'
```

**Response**
```json
{"prediction": [1]}
```

| Output | Meaning |
|---|---|
| `0` | Ham (legitimate message) |
| `1` | Spam |

---

## Authentication Flow

```
1. POST /auth/signup       →  create account
2. POST /api-key/create    →  receive raw API key
3. POST /predict           →  pass key in X-API-KEY header
```

API keys are stored as Argon2id hashes. On each request, keys are looked up by an 8-character plaintext prefix for efficiency, then verified against the stored hash.

---

## ML Model

The spam detector is a scikit-learn `Pipeline` consisting of:

1. **TF-IDF Vectorizer** — binary term weighting, English stop words removed, sublinear TF scaling
2. **MLP Classifier** — architecture `(20, 30, 20)`, trained for up to 4000 iterations with L2 regularization (`alpha=0.1`)

Trained on the UCI SMS Spam Collection dataset (~5500 messages). To evaluate the saved model against the held-out test set:

```bash
python -m ml.test
```
