# Development Setup Guide

## Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (for PostgreSQL and Redis)
- Git

## Backend Setup

### 1. Setup Python Environment

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env` with:
- **Zoho Books API Credentials** (get these from your Zoho account)
  - `ZOHO_CLIENT_ID`
  - `ZOHO_CLIENT_SECRET`
  - `ZOHO_REFRESH_TOKEN`
  - `ZOHO_ORGANIZATION_ID`
- **Claude API Key**
  - `ANTHROPIC_API_KEY` (get from https://console.anthropic.com)
- **JWT Secret** (generate a secure random string)

### 3. Start PostgreSQL and Redis

```bash
# From project root
docker-compose -f docker-compose.dev.yml up -d

# Verify they're running
docker-compose -f docker-compose.dev.yml ps
```

### 4. Initialize Database

The database will be initialized automatically when you start the app, but you can also do it manually:

```bash
python -c "from app.db.database import init_db; init_db()"
```

### 5. Run Backend Server

```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`
- API docs (Swagger): `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

## Frontend Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment Variables

Create `.env.local`:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Run Development Server

```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Testing Zoho Sync Manually

Once the backend is running, you can test the sync manually:

```bash
# Trigger a delta sync (incremental)
python -c "
from app.services.zoho_sync import ZohoSyncService
service = ZohoSyncService()
result = service.sync_all(full_sync=False)
print('Sync result:', result)
"

# Or trigger a full sync
python -c "
from app.services.zoho_sync import ZohoSyncService
service = ZohoSyncService()
result = service.sync_all(full_sync=True)
print('Sync result:', result)
"
```

## Checking Database

Connect to PostgreSQL to verify data:

```bash
# Connect to the local database
psql -h localhost -U postgres -d bi_system

# View sync history
SELECT * FROM sync_history ORDER BY started_at DESC LIMIT 10;

# View customers
SELECT COUNT(*) FROM customers;
SELECT * FROM customers LIMIT 5;

# View invoices
SELECT COUNT(*) FROM invoices;
```

## Troubleshooting

### PostgreSQL Connection Issues

```bash
# Check if PostgreSQL is running
docker-compose -f docker-compose.dev.yml logs postgres

# Restart services
docker-compose -f docker-compose.dev.yml restart postgres
```

### Zoho API Errors

1. Verify credentials in `.env` are correct
2. Check that refresh token is still valid (Zoho tokens expire)
3. Review API response in logs for specific errors

### Scheduler Not Running

The scheduler starts automatically with the FastAPI app. Check logs for:

```
"Scheduler started at"
"Jobs scheduled:"
```

## Project Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Configuration (reads .env)
│   ├── db/
│   │   ├── database.py         # SQLAlchemy setup + session management
│   │   └── migrations/         # Alembic migrations (future)
│   ├── models/
│   │   └── database.py         # SQLAlchemy ORM models
│   ├── services/
│   │   ├── zoho_api_client.py  # Zoho API client (OAuth + requests)
│   │   └── zoho_sync.py        # Sync orchestration (incremental/full)
│   ├── jobs/
│   │   └── scheduler.py        # APScheduler setup (hourly + weekly sync)
│   ├── utils/
│   │   └── logger.py           # Structured logging
│   └── api/                    # API endpoints (coming in Phase 2)
└── requirements.txt            # Python dependencies
```

## Next Steps

1. ✅ Backend foundation set up
2. ✅ Zoho API integration ready
3. ✅ Scheduler configured (hourly sync + weekly full sync)
4. **Next**: Test sync with sample data from Zoho
5. **Then**: Build dashboard API endpoints (Phase 2)
