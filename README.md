# AI-Powered Business Intelligence System

A comprehensive BI platform that aggregates data from multiple sources (Zoho Books, QuickBooks, Stripe, custom databases) and provides intelligent, dynamic reporting through an AI-powered chat interface.

## Features

- 📊 **Automated Data Sync** - Hourly incremental + weekly full syncs from Zoho Books
- 🚀 **Modern Dashboard** - Real-time metrics and visualizations
- 💬 **AI-Powered Q&A** - Ask natural language questions about your business data
- 📈 **Dynamic Reports** - Generate custom reports on-demand
- 🔒 **Enterprise-Ready** - Secure, scalable, production-ready architecture

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | React/Next.js + TypeScript + Tailwind CSS |
| **Backend** | Python + FastAPI + SQLAlchemy |
| **Database** | PostgreSQL |
| **Cache** | Redis |
| **AI/LLM** | Claude API |
| **Scheduling** | APScheduler |
| **Hosting** | Vercel (frontend) + Render (backend) |

## Project Status

**Phase 1: Foundation** ✅ **IN PROGRESS**
- ✅ Database schema designed
- ✅ Zoho API integration
- ✅ Data sync pipeline (incremental + full)
- ✅ Scheduler configured
- ⏳ Testing with real Zoho data

**Phase 2: Backend APIs** (Weeks 4-6)
- Dashboard endpoints (revenue, growth, top products)
- LLM query execution engine
- Auth middleware

**Phase 3: Frontend** (Weeks 7-9)
- Dashboard UI with charts
- Chat interface for Q&A
- Real-time report generation

**Phase 4: Production** (Weeks 10-12)
- Testing & optimization
- Deployment pipeline
- Monitoring & alerts

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Zoho Books API credentials
- Claude API key

### 1. Setup Backend

```bash
# Install dependencies
make backend-install

# Start PostgreSQL and Redis
make docker-up

# Initialize database
make db-init

# Create .env file (copy from .env.example)
cp backend/.env.example backend/.env
# Edit backend/.env with your credentials

# Run backend server
make backend-run
```

Backend will be available at `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`

### 2. Setup Frontend

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Run dev server
npm run dev
```

Frontend will be available at `http://localhost:3000`

## Database Schema

The system uses a normalized PostgreSQL schema with these core tables:

- **customers** - Customer information from Zoho
- **products** - Product/item catalog
- **invoices** - Invoices with line items
- **payments** - Payment records
- **daily_revenue** - Aggregated daily metrics
- **product_sales** - Monthly product sales aggregations
- **sync_history** - Data sync audit trail
- **query_history** - AI query execution log

## API Endpoints

### Dashboard
```
GET  /api/dashboard/metrics         # Key metrics (revenue, invoices, etc)
GET  /api/dashboard/revenue-trend   # Revenue over time
GET  /api/dashboard/top-products    # Best-selling products
GET  /api/dashboard/growth-rate     # Growth metrics
```

### LLM Queries
```
POST /api/query/chat                # Ask natural language questions
GET  /api/query/history             # Query execution history
```

### System
```
GET  /api/health                    # Health check
POST /api/sync/trigger              # Manually trigger sync
GET  /api/sync/status/{sync_id}    # Check sync status
```

## Data Sync

**Automatic Schedules:**
- ⏰ **Hourly (00:00)** - Delta sync (only changed records)
- 📅 **Weekly (Sunday 00:00)** - Full sync (all records)

**Manual Trigger:**
```bash
python -c "
from app.services.zoho_sync import ZohoSyncService
service = ZohoSyncService()
result = service.sync_all(full_sync=False)
"
```

## Configuration

All configuration via environment variables (see `backend/.env.example`):

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/bi_system

# Zoho Books
ZOHO_CLIENT_ID=your_client_id
ZOHO_CLIENT_SECRET=your_client_secret
ZOHO_REFRESH_TOKEN=your_refresh_token
ZOHO_ORGANIZATION_ID=your_org_id

# Claude API
ANTHROPIC_API_KEY=your_api_key

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=your-secret-key
JWT_EXPIRATION_HOURS=24
```

## Monitoring & Logging

- **Logs** - JSON structured logs to stdout (can be redirected to log aggregators)
- **Sync History** - Track all sync events in `sync_history` table
- **Query Audit** - All LLM queries logged in `query_history` table
- **Health Checks** - Built-in `/health` endpoint for monitoring

## Development

### Useful Commands

```bash
make help              # Show all commands
make lint              # Run code linters
make format            # Format code with black
make backend-test      # Run tests
make db-shell          # Connect to PostgreSQL
make docker-logs       # View Docker logs
```

### Project Structure

```
.
├── backend/                    # Python FastAPI application
│   ├── app/
│   │   ├── main.py             # FastAPI entry point
│   │   ├── config.py           # Configuration
│   │   ├── db/                 # Database layer
│   │   ├── models/             # SQLAlchemy ORM models
│   │   ├── services/           # Business logic
│   │   │   ├── zoho_api_client.py
│   │   │   └── zoho_sync.py
│   │   ├── api/                # API endpoints (coming)
│   │   ├── jobs/               # Scheduled jobs
│   │   └── utils/              # Utilities
│   └── requirements.txt        # Dependencies
│
├── frontend/                   # React/Next.js application
│   ├── src/
│   │   ├── pages/
│   │   ├── components/
│   │   ├── hooks/
│   │   └── services/
│   └── package.json
│
├── docs/                       # Documentation
│   ├── SETUP.md               # Setup guide
│   ├── API.md                 # API docs
│   └── ARCHITECTURE.md        # Architecture decisions
│
├── infra/                      # Infrastructure configs
│   ├── docker-compose.yml     # Production
│   └── postgres/
│
├── docker-compose.dev.yml     # Development
├── Makefile                   # Common commands
└── README.md                  # This file
```

## Documentation

- **[SETUP.md](docs/SETUP.md)** - Detailed setup instructions
- **[IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md)** - Full project plan
- **[API.md](docs/API.md)** - API reference (coming)
- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Architecture decisions (coming)

## Roadmap

### Phase 1: Foundation ✅
Data pipeline from Zoho to PostgreSQL with automatic sync

### Phase 2: Backend (Next)
Dashboard APIs and LLM integration for SQL generation

### Phase 3: Frontend
React dashboard and chat interface

### Phase 4: Production
Testing, deployment, monitoring

### Phase 5: Expansion
Add Stripe, QuickBooks, sub-product data sources

## Deployment

### Hosting Recommendations

- **Frontend**: Vercel (Next.js native, free tier available)
- **Backend**: Render (Docker-based, $7-15/month)
- **Database**: Render PostgreSQL or AWS RDS ($7-15/month)
- **Cache**: Render Redis ($12-25/month)

**Estimated Monthly Cost**: $14-30

### Deploy Backend to Render

```bash
# Create Render account and connect GitHub
# Add environment variables in Render dashboard
# Push to main branch -> automatic deployment
```

### Deploy Frontend to Vercel

```bash
# Create Vercel account and connect GitHub
# Add NEXT_PUBLIC_API_URL environment variable
# Push to main branch -> automatic deployment
```

## Contributing

1. Create a feature branch (`git checkout -b feature/amazing-feature`)
2. Make your changes
3. Run tests and linting (`make lint`)
4. Commit with descriptive messages
5. Push and create a pull request

## Support

For issues, questions, or feedback:
- Open an issue on GitHub
- Check the documentation in `docs/`
- Review the implementation plan for architectural context

## License

[Your License Here]

---

**Current Phase**: Foundation (Phase 1)
**Last Updated**: 2026-07-12
**Maintainer**: Solo Developer Mode ✨
