# IntelliTrace Backend – Getting Started

## Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker + Docker Compose (optional, easiest path)

---

## Option A – Docker Compose (Recommended)

```bash
cd backend
docker-compose up --build
```

This starts:
- **FastAPI** on `http://localhost:8000`
- **PostgreSQL** on `localhost:5432`
- **Redis** on `localhost:6379`
- **Celery worker** (fraud scoring)
- **Flower** (Celery monitor) on `http://localhost:5555`

Then seed the database:
```bash
docker-compose exec api python seed_db.py
```

---

## Option B – Local Dev (no Docker)

### 1. Install dependencies
```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure environment
Copy `.env.example` to `.env` and update values if needed.
Defaults match a local PostgreSQL with user `intellitrace` / password `intellitrace_secret`.

### 3. Create the database
```sql
-- In psql:
CREATE USER intellitrace WITH PASSWORD 'intellitrace_secret';
CREATE DATABASE intellitrace OWNER intellitrace;
```

### 4. Run migrations (creates all tables)
```bash
# The app auto-creates tables on startup via init_db().
# OR use Alembic for proper migrations:
alembic upgrade head
```

### 5. Seed the database
```bash
python seed_db.py
# To reset and reseed:
python seed_db.py --reset
```

### 6. Start the API
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 7. Start the Celery worker (separate terminal)
```bash
celery -A celery_worker.celery_app worker --loglevel=info --concurrency=2
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/docs` | Swagger UI |
| GET | `/api/dashboard` | KPIs, charts, sparklines |
| POST | `/api/invoices` | Submit invoice → triggers fraud scoring |
| GET | `/api/invoices` | List flagged invoices |
| GET | `/api/invoices/{id}` | Invoice detail + risk breakdown |
| GET | `/api/suppliers` | List all suppliers |
| GET | `/api/suppliers/{id}` | Supplier profile + charts |
| POST | `/api/suppliers` | Create supplier |
| GET | `/api/alerts` | List alerts (filterable) |
| PATCH | `/api/alerts/{id}` | Update alert status |
| GET | `/api/graph` | Supply chain network graph |

---

## Fraud Scoring Pipeline

When a new invoice is submitted:
1. **FastAPI** saves it and dispatches a **Celery task** (`compute_fraud_score`)
2. The task fetches the supplier's full invoice history and builds a **NetworkX graph**
3. **Feature engineering** extracts 7 normalized features (revenue ratio, velocity, etc.)
4. **PyTorch MLP** runs inference → `ml_probability ∈ [0, 1]`
5. **Rule-based detectors** check for: revenue mismatch, velocity anomaly, duplicate financing, PO mismatch, cascade depth, carousel cycles
6. Combined score = `(ml_prob × 45) + (rules_avg × 55)` → `fraud_score ∈ [0, 100]`
7. Alerts are generated for any triggered rules if `fraud_score ≥ 55`
