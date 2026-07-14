# Quick Start Guide - Phase 1 Foundation Ready

## 1️⃣ Prerequisites
- Python 3.11+, Node.js 18+, Docker Desktop installed
- Zoho Books API credentials (OAuth Client ID, Secret, Refresh Token, Organization ID)
- Claude API key (from console.anthropic.com)

## 2️⃣ One-Time Setup (5 minutes)

```bash
# Clone/navigate to project
cd "d:\AI projects\BI"

# Copy and configure environment
copy backend\.env.example backend\.env
# Edit backend/.env with:
#   - ZOHO_CLIENT_ID, ZOHO_CLIENT_SECRET, ZOHO_REFRESH_TOKEN, ZOHO_ORGANIZATION_ID
#   - ANTHROPIC_API_KEY
#   - JWT_SECRET_KEY (can be any random string for now)

# One-command setup
make setup
# This does:
#   - pip install -r requirements.txt
#   - docker-compose up -d (PostgreSQL + Redis)
#   - Initialize database schema
```

## 3️⃣ Start Developing

**Terminal 1 - Run backend:**
```bash
make backend-run
```
✅ Opens http://localhost:8000 (API Docs at /docs, Health at /health)
✅ Scheduler starts automatically (check logs for "Scheduler started")

**Terminal 2 - Setup frontend (Phase 3, not ready yet):**
```bash
cd frontend
npm install
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
npm run dev
```

## 4️⃣ Test the Sync (Right Now!)

```bash
# Option A: Wait for automatic sync
# Hourly at :00 minutes, weekly Sunday at 00:00

# Option B: Trigger manually
python -c "
from app.services.zoho_sync import ZohoSyncService
sync = ZohoSyncService()
result = sync.sync_all(full_sync=False)
print('Sync result:', result)
"

# Option C: Check what got synced
make db-shell
# Then run:
SELECT * FROM sync_history ORDER BY started_at DESC LIMIT 10;
SELECT COUNT(*) as customer_count FROM customers;
SELECT COUNT(*) as invoice_count FROM invoices;
```

## 5️⃣ What You Have Now

✅ **Automatic hourly sync** from Zoho → PostgreSQL
✅ **Weekly full sync** for reconciliation  
✅ **Health checks** at http://localhost:8000/health
✅ **Structured logging** to stdout
✅ **Sync audit trail** in database
✅ **Ready for Phase 2** backend APIs

## Common Commands

```bash
make help              # Show all available commands
make backend-run       # Run the FastAPI server
make docker-up         # Start PostgreSQL + Redis
make docker-down       # Stop PostgreSQL + Redis
make db-init           # Initialize/reset database
make db-shell          # Connect to PostgreSQL
make lint              # Check code style
make format            # Format code
```

## Next: Phase 2 (Backend APIs)

When ready to build dashboard APIs:

1. Create `backend/app/services/dashboard_service.py` - queries for metrics
2. Create `backend/app/api/dashboard.py` - FastAPI endpoints
3. Create `backend/app/services/llm_service.py` - Claude integration
4. Create `backend/app/api/query.py` - Chat endpoint

See IMPLEMENTATION_PLAN.md for details.

## Troubleshooting

### PostgreSQL won't connect
```bash
docker-compose -f docker-compose.dev.yml logs postgres
docker-compose -f docker-compose.dev.yml restart postgres
```

### Zoho sync fails
- Check `.env` has correct credentials
- Verify Zoho OAuth app is active
- Check logs for specific API errors

### Scheduler not running
- Ensure FastAPI app started successfully
- Check logs for "Scheduler started at"

## Support

- 📖 Full setup: `docs/SETUP.md`
- 📋 Implementation plan: `IMPLEMENTATION_PLAN.md`
- 🏗️ Architecture: `docs/ARCHITECTURE.md`

---

**Status**: Ready to develop! 🚀
**Next phase**: Build dashboard APIs (Phase 2)
