# Code Review — ML Model API

> Reviewed against FastAPI production best practices (2024–2026).  
> Covers architecture, security, correctness, performance, and maintainability.

---

## Table of Contents

1. [What's Done Well](#1-whats-done-well)
2. [Areas for Improvement](#2-areas-for-improvement)
   - [Critical / Bugs](#21-critical--bugs)
   - [Security](#22-security)
   - [Architecture & Design](#23-architecture--design)
   - [Performance](#24-performance)
   - [Code Quality](#25-code-quality)
   - [ML / Data](#26-ml--data)
   - [Tooling & Ops](#27-tooling--ops)
3. [Summary Table](#3-summary-table)

---

## 1. What's Done Well

### ✅ Clean layer separation
The project properly separates concerns across `routers/`, `services/`, `schemas/`, `models/`, and `core/`. Routers stay thin — they validate input, call a service, and return a response. Business logic lives in services. This is the recommended FastAPI pattern and makes the codebase easy to navigate and test.

### ✅ Argon2id for credential hashing
Using `argon2-cffi` with tuned parameters (`time_cost=2`, `memory_cost=65536`, `parallelism=2`) is a solid choice. Argon2id is the current OWASP-recommended password hashing algorithm — stronger than bcrypt or PBKDF2. The same hasher is correctly reused for both passwords and API keys.

### ✅ Prefix-based API key lookup
Storing an 8-character plaintext prefix alongside the hash is a well-known pattern (used by GitHub, Stripe) that avoids a full table scan on every request. Looking up by prefix first, then verifying the hash, is efficient and correct.

### ✅ `secrets.token_urlsafe` for key generation
Using the `secrets` module (cryptographically secure RNG) rather than `random` or `uuid4` for API key generation is the right call.

### ✅ Pydantic settings with `.env` support
`pydantic-settings` with `lru_cache` is idiomatic FastAPI. Settings are typed, validated on startup, and cached — no raw `os.getenv()` scattered through the codebase.

### ✅ Modern SQLAlchemy ORM style
Using `Mapped` / `mapped_column` (SQLAlchemy 2.0 style) with proper type annotations is current best practice. Relationships are declared cleanly with `back_populates`.

### ✅ Usage tracking
Recording every API call in the `Record` table is a good foundation for rate limiting, billing, and audit trails.

### ✅ `is_active` flag on API keys
Soft-delete / revocation support is built in from the start. Keys can be deactivated without being deleted, which preserves audit history.

### ✅ scikit-learn Pipeline
Wrapping the TF-IDF vectorizer and MLP classifier into a single `Pipeline` object means the vectorizer is fit only on training data and the same transformation is guaranteed at inference time — no train/serve skew.

### ✅ Stratified train/test split
Using `stratify=y` in `train_test_split` ensures class proportions are preserved in both splits, which matters on imbalanced datasets like spam corpora.

---

## 2. Areas for Improvement

### 2.1 Critical / Bugs

#### 🔴 Wrong type annotation on `APIKey.key` and `APIKey.prefix`
```python
# app/models/api_key.py — current (wrong)
key: Mapped[int] = mapped_column(String(50), ...)
prefix: Mapped[int] = mapped_column(String(8), ...)
```
Both columns store strings but are annotated as `Mapped[int]`. SQLAlchemy will still work at runtime because it trusts the column type, but mypy/pyright will flag every access to these fields, and it's misleading. Fix:
```python
key: Mapped[str] = mapped_column(String(100), ...)
prefix: Mapped[str] = mapped_column(String(8), ...)
```
The `key` column also needs to be wider — an Argon2id hash is ~95 characters, but the column is `String(50)`.

#### 🔴 `ph.verify` in `api_key` router raises unhandled exception
```python
# app/routers/api_key.py
ph.verify(user.password, req.password)
```
If the password is wrong, `ph.verify` raises `VerifyMismatchError` (and potentially `VerifyMismatchError`, `VerificationError`, or `InvalidHashError`). There is no `try/except` here, so a wrong password returns a raw 500 error instead of a 401. Fix:
```python
from argon2.exceptions import VerifyMismatchError

try:
    ph.verify(user.password, req.password)
except VerifyMismatchError:
    raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail='Invalid credentials')
```

#### 🔴 Inverted train/test split ratio
```python
# ml/train.py
X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=0.3, ...)
```
`train_size=0.3` means the model trains on **30%** of the data and evaluates on 70%. The conventional split is 70–80% train. This significantly limits model quality. Change to `train_size=0.8`.

#### 🔴 Model loaded at module import time in router
```python
# app/routers/predict.py
model = joblib.load('ml/models/spam_detector.pkl')
```
This path is relative to the working directory, so if the server is started from any directory other than the project root it will crash. It also runs at import time with no error handling. The correct approach is to load the model once at startup using a lifespan context:
```python
# app/main.py
from contextlib import asynccontextmanager
import joblib

ml_model = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    ml_model['spam'] = joblib.load('ml/models/spam_detector.pkl')
    yield
    ml_model.clear()

app = FastAPI(lifespan=lifespan)
```
Then inject or access `ml_model['spam']` in the router.

---

### 2.2 Security

#### 🟠 No rate limiting
Any unauthenticated actor can hammer `/auth/signup` and `/api-key/create` indefinitely. This enables credential stuffing and resource exhaustion. Add rate limiting with `slowapi` (the standard FastAPI solution):
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post('/signup')
@limiter.limit('5/minute')
async def signup(request: Request, ...):
    ...
```

#### 🟠 Timing attack on username enumeration
```python
# app/routers/api_key.py
user = get_user_by_username(req.username, db)
if not user:
    raise HTTPException(401, detail='Username does not exists')
```
Returning a different response for "user not found" vs "wrong password" allows an attacker to enumerate valid usernames. Use a single generic message: `'Invalid credentials'` for both cases. Also run `ph.verify` even on a dummy hash when the user doesn't exist, to prevent timing-based enumeration:
```python
if not user:
    ph.verify(DUMMY_HASH, req.password)  # constant-time dummy check
    raise HTTPException(401, detail='Invalid credentials')
```

#### 🟠 No CORS configuration
No `CORSMiddleware` is configured. Any browser-based client from any origin can call this API. If this is intended to be consumed only by specific frontends, restrict origins explicitly. At minimum, document the decision.

#### 🟠 `DEBUG` flag in settings is unused
The `debug: bool` setting is read but never applied to the FastAPI app or logging. In debug mode FastAPI will expose full tracebacks in HTTP responses. Either wire it up:
```python
app = FastAPI(debug=get_settings().debug)
```
or remove the setting to avoid a false sense of security control.

#### 🟡 No `WWW-Authenticate` header on 401 responses
The HTTP spec says 401 responses should include a `WWW-Authenticate` header identifying the auth scheme. FastAPI's `HTTPBearer` does this automatically, but manual `HTTPException(401)` does not:
```python
raise HTTPException(
    status.HTTP_401_UNAUTHORIZED,
    detail='Invalid API key',
    headers={'WWW-Authenticate': 'ApiKey'}
)
```

#### 🟡 API key column too short for Argon2 hashes
As noted above — `String(50)` will silently truncate Argon2id hashes (~95 chars) depending on the database. SQLite is permissive but PostgreSQL would hard-fail. Use `String(200)` to be safe.

---

### 2.3 Architecture & Design

#### 🟠 `get_user_by_username` is duplicated
The same function exists in both `services/auth.py` and `services/api_key.py`. Extract it to a shared location, e.g. `services/user.py` or `repositories/user.py`:
```python
# app/services/user.py
def get_user_by_username(username: str, db: Session) -> User | None:
    return db.query(User).where(User.username == username).first()
```

#### 🟠 Router function named `signup` in `api_key.py`
```python
# app/routers/api_key.py
async def signup(req: AuthRequest, ...):
```
The function that creates an API key is named `signup`. This is a copy-paste artifact that causes confusion in stack traces, OpenAPI docs, and logs. Rename it to `create_api_key`.

#### 🟠 No API versioning
There's no `/v1/` prefix. When you need to make breaking changes, you'll have no way to do it without forcing all clients to update simultaneously. Add versioning from the start:
```python
app.include_router(auth.router, prefix='/v1')
app.include_router(api_key.router, prefix='/v1')
app.include_router(predict.router, prefix='/v1')
```

#### 🟡 `role` field exists but is never used
`APIKey.role` (`'user'` | `'admin'`) is defined in the model but there's no authorization logic that reads it. Either implement role-based access control or remove the field to reduce confusion.

#### 🟡 No login endpoint
Users can sign up and generate API keys, but there's no `POST /auth/login` endpoint returning a session token. The `/api-key/create` route doubles as a login, which is semantically odd. Consider separating concerns: a login endpoint for verifying identity, and a separate key management endpoint.

#### 🟡 `dependencies.py` is a re-export module of mixed concerns
`dependencies.py` re-exports `get_db`, `get_settings`, `ph`, and `validate_api_key` from their respective modules. This flattens the dependency graph and introduces circular import risk (e.g., `security.py` imports `get_db` from `dependencies.py` which imports from `security.py`). Import directly from source modules in routers/services instead.

#### 🟡 `app/models/__init__.py` — unclear what it exports
The `models/__init__.py` has imports (e.g., `from app.models import User`) used throughout, but the file was not in the tree with content shown. Ensure it explicitly exports all models to avoid wildcard-style implicit imports.

---

### 2.4 Performance

#### 🟠 Synchronous SQLAlchemy with `async` route handlers
All routes are declared `async def` but use synchronous SQLAlchemy (`Session`, `create_engine`). Synchronous DB calls block the event loop, negating the concurrency benefits of async FastAPI. The proper fix is to use `AsyncSession` and `create_async_engine` from SQLAlchemy 2.0 with an async driver (`aiosqlite` for SQLite):
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

engine = create_async_engine('sqlite+aiosqlite:///./database.db')
```
Alternatively, if keeping sync SQLAlchemy, declare routes as plain `def` (not `async def`) — FastAPI will run them in a thread pool automatically, which is safer than blocking the event loop:
```python
@router.post('/predict')
def predict(req: PredictRequest, ...):  # sync, runs in threadpool
    ...
```

#### 🟡 ML inference blocks the event loop
`model.predict(req.X_data)` is a CPU-bound call running in an async route handler. This blocks the event loop for the duration of inference. For short TF-IDF + MLP predictions this may be acceptable, but the correct pattern is to offload to a thread pool:
```python
import asyncio
prediction = await asyncio.get_event_loop().run_in_executor(
    None, model.predict, req.X_data
)
```

#### 🟡 No database connection pooling configuration
The SQLAlchemy engine is created with default pool settings. For SQLite this is fine, but if you ever migrate to PostgreSQL you'll want to configure `pool_size`, `max_overflow`, and `pool_pre_ping=True`. Adding `pool_pre_ping=True` now is a low-cost safeguard against stale connections.

---

### 2.5 Code Quality

#### 🟠 No tests
There are no unit or integration tests (`pytest` is not in `requirements.txt`). This is the single largest maintainability gap. At minimum, add tests for:
- `validate_api_key` (valid key, invalid key, inactive key)
- `POST /auth/signup` (success, duplicate username)
- `POST /predict` (valid key + spam input, valid key + ham input, no key)

FastAPI's `TestClient` makes this straightforward:
```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get('/health')
    assert response.status_code == 200
```

#### 🟠 No logging
There is no structured logging anywhere. When something goes wrong in production you'll have no visibility. Add a logger at the app level:
```python
import logging
logger = logging.getLogger(__name__)

logger.info('Prediction requested', extra={'api_key_prefix': db_key.prefix})
```
Consider `structlog` or Python's built-in `logging` with JSON formatting for production.

#### 🟠 Unpinned dependencies
```
fastapi[standard]
sqlalchemy
argon2-cffi
```
No versions are pinned. A `pip install` six months from now may pull in a breaking release. Pin all dependencies:
```
fastapi[standard]==0.115.0
sqlalchemy==2.0.35
argon2-cffi==23.1.0
scikit-learn==1.5.2
```
Or use a lockfile tool like `pip-tools` (`requirements.in` → `requirements.txt`).

#### 🟡 `PredictResponse` example values are floats but type is `list[int]`
```python
class PredictResponse(BaseModel):
    prediction: list[int] = Field(..., example=[0.1, 0.4, 0.5])
```
The example shows floats `[0.1, 0.4, 0.5]` but the model returns binary integer labels `[0, 1]`. The example will mislead anyone reading the OpenAPI docs. Fix:
```python
prediction: list[int] = Field(..., example=[0, 1])
```

#### 🟡 `field` deprecated `example` kwarg (Pydantic v2)
In Pydantic v2, the `example` parameter on `Field` is deprecated in favour of `json_schema_extra`:
```python
prediction: list[int] = Field(..., json_schema_extra={'example': [0, 1]})
```

#### 🟡 `AuthResponse` includes a `'failure'` literal that's never returned
```python
class AuthResponse(BaseModel):
    status: Literal['success', 'failure']
```
The signup handler either returns `'success'` or raises an `HTTPException`. The `'failure'` variant is dead code that confuses callers reading the schema.

#### 🟡 No `app` metadata in `FastAPI()` constructor
```python
app = FastAPI()
```
OpenAPI docs will have no title, description, or version. Add them:
```python
app = FastAPI(
    title='Spam Detector API',
    description='SMS spam classification via a TF-IDF + MLP model.',
    version='1.0.0',
)
```

#### 🟡 Trailing comma in `mapped_column` calls
```python
prefix: Mapped[int] = mapped_column(
    String(8),
    nullable=False,      # ← trailing comma with no further arguments
)
```
Not a bug, but inconsistent across the models. Some have it, some don't.

---

### 2.6 ML / Data

#### 🟠 LabelEncoder not saved alongside the model
The `LabelEncoder` is fit in `train.py` to map `ham`/`spam` → 0/1, but only the `Pipeline` is saved. The mapping is implicit: whatever order `LabelEncoder.fit_transform` assigns is baked in. If the dataset column order ever changes, predictions could silently swap (spam=0, ham=1). Save the encoder or document the label mapping explicitly:
```python
# In train.py
joblib.dump({'pipeline': pipe, 'label_encoder': le}, 'ml/models/spam_detector.pkl')
```

#### 🟠 No input validation on prediction payload size
A client can send thousands of messages in a single request. Add a `max_length` on `X_data`:
```python
X_data: list[str] = Field(..., min_length=1, max_length=100, alias='X-data')
```
Also consider capping individual message length.

#### 🟡 No model versioning or metadata
The `spam_detector.pkl` file has no attached metadata (training date, dataset version, accuracy, sklearn version). A `pickle`/`joblib` file built against one version of scikit-learn can silently fail or give different results on another version. Store model metadata:
```python
metadata = {
    'model': pipe,
    'trained_at': datetime.utcnow().isoformat(),
    'sklearn_version': sklearn.__version__,
    'accuracy': pipe.score(X_test, y_test),
}
joblib.dump(metadata, 'ml/models/spam_detector.pkl')
```

#### 🟡 `ml/test.py` runs at module level (not inside `if __name__`)
```python
# ml/test.py — top-level code
model = joblib.load(...)
y_pred = model.predict(X_test)
```
All evaluation code runs on import. Wrap it in `if __name__ == '__main__':` like `train.py` does.

---

### 2.7 Tooling & Ops

#### 🟠 No Docker / containerisation
There's no `Dockerfile` or `docker-compose.yml`. For any non-trivial deployment you'll need to containerise the app to ensure the Python environment, model file paths, and database location are reproducible.

#### 🟠 No database migrations
`init_db.py` uses `Base.metadata.create_all()` which only creates tables that don't exist. If you change a model (add a column, rename a field), you have no migration path — you'd need to drop and recreate the database. Use **Alembic** from day one:
```bash
pip install alembic
alembic init alembic
```

#### 🟡 `.env` file likely committed to git
There's a `.env` file in the project root. Ensure it's in `.gitignore`. Provide a `.env.example` with placeholder values instead:
```
DATABASE_URI=sqlite:///./database.db
DEBUG=false
```

#### 🟡 No `pyproject.toml` or project metadata
The project has `requirements.txt` but no `pyproject.toml`. For a Python project in 2025, `pyproject.toml` (with `uv`, `poetry`, or `hatch`) is the standard way to manage dependencies, dev tools (linters, formatters), and package metadata in one place.

#### 🟡 No linter / formatter configured
No `ruff`, `black`, or `flake8` configuration is present. Inconsistent spacing (e.g. `user=User(...)` vs `user = create_user(...)`) and mixed style would be caught automatically.

---

## 3. Summary Table

| Area | Finding | Severity |
|---|---|---|
| Type annotations | `APIKey.key` / `.prefix` typed as `Mapped[int]` not `Mapped[str]` | 🔴 Bug |
| Error handling | `ph.verify` raises unhandled exception on wrong password | 🔴 Bug |
| ML | Train/test split is 30/70 (inverted) | 🔴 Bug |
| Startup | Model loaded at import time with relative path | 🔴 Bug |
| Security | No rate limiting on auth endpoints | 🟠 High |
| Security | Username enumeration via error message + timing | 🟠 High |
| Security | `ph.verify` exception not caught in api_key router | 🟠 High |
| Architecture | `get_user_by_username` duplicated across services | 🟠 Medium |
| Architecture | Router function misnamed (`signup` in api_key router) | 🟠 Medium |
| Architecture | No API versioning | 🟠 Medium |
| Performance | Sync SQLAlchemy inside `async def` blocks event loop | 🟠 Medium |
| Quality | No tests | 🟠 Medium |
| Quality | No logging | 🟠 Medium |
| Quality | Unpinned dependencies | 🟠 Medium |
| ML | LabelEncoder not saved with model | 🟠 Medium |
| ML | No input size cap on prediction payload | 🟠 Medium |
| Security | `DEBUG` flag defined but never wired up | 🟡 Low |
| Security | Missing `WWW-Authenticate` header on 401s | 🟡 Low |
| Security | API key column too short for Argon2 hashes | 🟡 Low |
| Architecture | `role` field exists but is unused | 🟡 Low |
| Quality | `PredictResponse` example shows floats, type is int | 🟡 Low |
| Quality | `AuthResponse` has unreachable `'failure'` literal | 🟡 Low |
| Quality | No `FastAPI()` metadata (title, version) | 🟡 Low |
| ML | `ml/test.py` code runs at module level | 🟡 Low |
| ML | No model versioning / metadata stored | 🟡 Low |
| Ops | No Docker setup | 🟠 Medium |
| Ops | No database migrations (Alembic) | 🟠 Medium |
| Ops | `.env` may be committed to git | 🟡 Low |
| Ops | No linter/formatter configured | 🟡 Low |

---

*References: [FastAPI official docs](https://fastapi.tiangolo.com), [zhanymkanov/fastapi-best-practices](https://github.com/zhanymkanov/fastapi-best-practices), [auth0 FastAPI Best Practices](https://auth0.com/blog/fastapi-best-practices/), [OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)*
