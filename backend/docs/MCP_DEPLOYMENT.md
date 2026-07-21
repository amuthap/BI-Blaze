# QuickBooks MCP Deployment Guide

## Overview

The BlazeBI system integrates QuickBooks Online data using the official QuickBooks MCP (Model Context Protocol) server. This approach provides:

- **No custom OAuth maintenance**: MCP server handles all QB authentication internally
- **Pre-synced data**: Daily scheduled syncs populate the dashboard with QB data
- **Real-time queries**: Chat feature can query QB data via MCP when needed
- **Unified reporting**: Dashboard aggregates data from both Zoho Books and QuickBooks

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    BlazeBI Application                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              FastAPI Backend (Port 8000)             │   │
│  │  ┌────────────────────────────────────────────────┐  │   │
│  │  │  Scheduler (APScheduler)                       │  │   │
│  │  │  - Triggers daily QB sync at 02:00 UTC        │  │   │
│  │  │  - Triggers hourly Zoho sync                  │  │   │
│  │  └────────────────────────────────────────────────┘  │   │
│  │  ┌────────────────────────────────────────────────┐  │   │
│  │  │  QuickBooksMCPSync Service                    │  │   │
│  │  │  - Queries QB via MCP client                  │  │   │
│  │  │  - Populates QBCustomer, QBProduct, etc.      │  │   │
│  │  └────────────────────────────────────────────────┘  │   │
│  │  ┌────────────────────────────────────────────────┐  │   │
│  │  │  Chat Service                                 │  │   │
│  │  │  - Can query QB via QBQueryWrapper (optional) │  │   │
│  │  │  - Uses Claude LLM for natural language       │  │   │
│  │  └────────────────────────────────────────────────┘  │   │
│  │  ┌────────────────────────────────────────────────┐  │   │
│  │  │  Dashboard Service                            │  │   │
│  │  │  - Aggregates Zoho + QB data                  │  │   │
│  │  │  - Shows unified metrics and reports          │  │   │
│  │  └────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────┘   │
│                            ↓↑                                │
│  ┌──────────────────────────────────────────────────────┐   │
│  │           PostgreSQL Database                        │   │
│  │  - qb_customers, qb_products                         │   │
│  │  - qb_invoices, qb_invoice_line_items               │   │
│  │  - qb_payments                                       │   │
│  │  - (synced daily from QB via MCP)                    │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ↓
         ┌─────────────────────────────┐
         │  QB MCP Server Process      │
         │  (Python subprocess)        │
         │  - Handles QB OAuth         │
         │  - Queries QB Accounting API│
         │  - JSON-RPC communication   │
         └──────────────┬──────────────┘
                        │
                        ↓
         ┌──────────────────────────────┐
         │  Intuit QuickBooks API       │
         │  - Customers                 │
         │  - Invoices                  │
         │  - Items/Products            │
         │  - Payments                  │
         └──────────────────────────────┘
```

## Installation & Configuration

### 1. Install QB MCP Server

```bash
# On production server
pip install quickbooks-mcp

# Or from GitHub
git clone https://github.com/your-org/quickbooks-mcp.git
cd quickbooks-mcp
pip install -e .
```

### 2. Configure QB Credentials

Set environment variables in `.env`:

```bash
# Intuit OAuth credentials (from Intuit Developer Portal)
QB_CLIENT_ID=your_client_id
QB_CLIENT_SECRET=your_client_secret
QB_REDIRECT_URI=https://blazebi.hyperbig.com/oauth/callback

# QB Company/Realm ID (obtained from first authorization)
QB_REALM_ID=your_realm_id

# Alternatively, MCP server can use environment vars
export QB_CLIENT_ID=...
export QB_CLIENT_SECRET=...
```

### 3. Verify MCP Server Can Start

```bash
# Test locally
python -m quickbooks_mcp --port 3001

# Should output:
# MCP server listening on stdio...
```

### 4. Backend Configuration

Ensure backend has access to QB credentials:

```python
# backend/.env
QB_CLIENT_ID=...
QB_CLIENT_SECRET=...
QB_REDIRECT_URI=...
QB_REALM_ID=...
```

## Deployment Steps

### Step 1: Stop Current Application

```bash
ssh -i your-key.pem user@95.217.54.165
cd /home/BlazeBI/projects/BI-Blaze-Frontend

# Stop backend
pkill -f uvicorn

# Stop frontend if running
pkill -f node
```

### Step 2: Update Code

```bash
# Pull latest code
git pull origin main

# Install dependencies (if needed)
cd backend
pip install -r requirements.txt

cd ../frontend
npm install
```

### Step 3: Start Services

```bash
# Start backend with MCP support
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level info &

# Start frontend (optional, if using development frontend)
cd ../frontend
npm run dev &

# Or start nginx (if using production frontend)
sudo systemctl restart nginx
```

### Step 4: Verify Deployment

```bash
# Check backend health
curl http://localhost:8000/api/health

# Check scheduler status
# Logs should show scheduled jobs
tail -f /var/log/blazebi/backend.log

# Verify QB sync scheduled
grep "QB MCP Sync" /var/log/blazebi/backend.log
```

## Troubleshooting

### QB Sync Not Running

**Check if scheduler started:**
```bash
grep "Scheduler started" /var/log/blazebi/backend.log
grep "Jobs scheduled" /var/log/blazebi/backend.log
```

**Check if QB sync job exists:**
```bash
grep "qb_mcp_sync" /var/log/blazebi/backend.log
```

**Manual QB sync test:**
```python
# Connect to production database
python
from app.db.database import SessionLocal
from app.services.quickbooks_mcp import QuickBooksMCPSync
import asyncio

db = SessionLocal()
sync = QuickBooksMCPSync(db)
asyncio.run(sync.sync_all())
```

### MCP Server Connection Failed

**Error: "Failed to start QB MCP server"**

1. Verify MCP server is installed:
   ```bash
   python -m quickbooks_mcp --version
   ```

2. Check QB credentials are set:
   ```bash
   echo $QB_CLIENT_ID
   echo $QB_CLIENT_SECRET
   ```

3. Test MCP server manually:
   ```bash
   python -m quickbooks_mcp --port 3001
   # Try connecting from another shell
   ```

4. Check server logs:
   ```bash
   tail -f /var/log/quickbooks_mcp.log
   ```

### Database Errors

**Error: "ForeignKeyError" when syncing**

- Ensure QB customer is synced before invoice (customer_id foreign key)
- Sync order: customers → products → invoices → payments
- Check `/app/services/quickbooks_mcp.py` sync_all() order

**Error: "Connection refused" to PostgreSQL**

- Verify database is running: `systemctl status postgresql`
- Check connection string in backend `.env`
- Ensure database exists: `psql -U bi_user -d bi_system -c "SELECT 1"`

## Monitoring

### Daily Sync Status

Check logs for sync success/failure:

```bash
# Last 100 QB sync logs
grep "QB MCP Sync\|QB MCP sync" /var/log/blazebi/backend.log | tail -100

# Check sync timing
grep "Starting daily QB sync\|QB MCP sync completed" /var/log/blazebi/backend.log
```

### Database Record Counts

Monitor sync progress:

```bash
psql -U bi_user -d bi_system -c "
SELECT 
  (SELECT count(*) FROM qb_customers) as customers,
  (SELECT count(*) FROM qb_products) as products,
  (SELECT count(*) FROM qb_invoices) as invoices,
  (SELECT count(*) FROM qb_payments) as payments;
"
```

### Dashboard Data

Verify dashboard is showing QB data:

```bash
# Query aggregated dashboard data
curl http://localhost:8000/api/dashboard/metrics \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Future Enhancements

1. **Real-time Sync**: Implement QB webhooks for immediate updates
2. **Error Notifications**: Send alerts when sync fails
3. **Batch Operations**: Support bulk customer/invoice import
4. **Custom Queries**: Add QB query builder in Chat interface
5. **Multi-company**: Support multiple QB accounts/realms

## Support

For issues with:
- **MCP Server**: See QB MCP GitHub repository
- **Intuit API**: Check Intuit Developer Portal documentation
- **BlazeBI Integration**: Check backend logs and contact team

## References

- QB MCP GitHub: https://github.com/your-org/quickbooks-mcp
- Intuit Developer Portal: https://developer.intuit.com
- QB Accounting API Docs: https://developer.intuit.com/app/developer/qbo/docs/api
