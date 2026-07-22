# QB MCP Manual Deployment Guide

Since SSH key authorization isn't set up, please run these commands manually on the production server.

## SSH Into Production Server

```bash
ssh root@95.217.54.165
# Enter password when prompted
```

## Run Deployment Steps

Once logged in, run these commands:

### Step 1: Navigate to Project
```bash
cd /home/BlazeBI/projects/BI-Blaze-Frontend
pwd  # Should show: /home/BlazeBI/projects/BI-Blaze-Frontend
```

### Step 2: Pull Latest Code
```bash
git pull origin main
# Should show commit: d0c9aeb - Add comprehensive MCP deployment documentation
```

### Step 3: Install QB MCP Server
```bash
pip install quickbooks-mcp
# Should complete without errors
```

### Step 4: Verify QB Credentials
```bash
cd backend
cat .env | grep QB_
```

**Expected output:**
```
QB_CLIENT_ID=your_client_id
QB_CLIENT_SECRET=your_client_secret
QB_REALM_ID=your_realm_id
QB_REDIRECT_URI=https://blazebi.hyperbig.com/oauth/callback
```

⚠️ **If any are missing**, add them:
```bash
echo 'QB_CLIENT_ID=your_client_id' >> .env
echo 'QB_CLIENT_SECRET=your_client_secret' >> .env
echo 'QB_REALM_ID=your_realm_id' >> .env
echo 'QB_REDIRECT_URI=https://blazebi.hyperbig.com/oauth/callback' >> .env
```

### Step 5: Stop Current Backend
```bash
pkill -f uvicorn
sleep 2
echo "Backend stopped"
```

### Step 6: Start Backend with MCP Support
```bash
nohup python -m uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 2 \
    --log-level info \
    > /var/log/blazebi/backend.log 2>&1 &

sleep 5
echo "Backend started"
```

### Step 7: Verify Backend is Running
```bash
curl -s http://localhost:8000/api/health | jq .
# Should return: {"status":"ok", "app":"..."}
```

### Step 8: Check Scheduler
```bash
tail -50 /var/log/blazebi/backend.log | grep "Scheduler\|QB MCP\|Jobs scheduled"
```

**Expected output:**
```
Scheduler started at 2026-07-22 ...
Jobs scheduled:
  - Zoho Delta Sync (Hourly) (zoho_delta_sync): ...
  - Zoho Full Sync (Weekly) (zoho_full_sync): ...
  - QuickBooks MCP Sync (Daily) (qb_mcp_sync): ...
```

### Step 9: Check QB Database Status
```bash
psql -U bi_user -d bi_system << SQL
SELECT
  'qb_customers' as table_name, COUNT(*) as records FROM qb_customers
UNION ALL SELECT 'qb_products', COUNT(*) FROM qb_products
UNION ALL SELECT 'qb_invoices', COUNT(*) FROM qb_invoices
UNION ALL SELECT 'qb_invoice_line_items', COUNT(*) FROM qb_invoice_line_items
UNION ALL SELECT 'qb_payments', COUNT(*) FROM qb_payments
ORDER BY table_name;
SQL
```

**Expected output:**
```
table_name             | records
-----------------------+---------
qb_customers           |       0
qb_invoice_line_items  |       0
qb_invoices            |       0
qb_payments            |       0
qb_products            |       0
```

(Records will be 0 until sync runs)

### Step 10: Test QB Sync Manually (Optional)
```bash
python << 'PYTHON_EOF'
import asyncio
from app.db.database import SessionLocal
from app.services.quickbooks_mcp import QuickBooksMCPSync

print("Testing QB MCP sync...")
db = SessionLocal()
sync = QuickBooksMCPSync(db)

try:
    asyncio.run(sync.sync_all())
    print("✅ QB sync completed successfully!")
    
    # Check records
    from app.models.database import QBCustomer
    count = db.query(QBCustomer).count()
    print(f"QB Customers synced: {count}")
except Exception as e:
    print(f"❌ QB sync failed: {e}")
finally:
    db.close()
PYTHON_EOF
```

## Verification Checklist

After running the steps above, verify:

- [ ] Code pulled (commit d0c9aeb visible in `git log`)
- [ ] QB MCP installed (`pip show quickbooks-mcp`)
- [ ] QB credentials in `.env` file
- [ ] Backend running (`curl http://localhost:8000/api/health` returns OK)
- [ ] Scheduler started (check logs for "Scheduler started")
- [ ] QB tables exist (`SELECT COUNT(*) FROM qb_customers;` returns 0 or more)
- [ ] QB sync job registered (check logs for "qb_mcp_sync")

## Monitoring

### Watch Backend Logs
```bash
tail -f /var/log/blazebi/backend.log
```

### Check QB Sync Tomorrow
At 02:00 UTC tomorrow, check:
```bash
grep "QB MCP Sync\|QB MCP sync" /var/log/blazebi/backend.log | tail -20
```

### Manual Sync Trigger
To sync on-demand:
```bash
cd /home/BlazeBI/projects/BI-Blaze-Frontend/backend
python << 'EOF'
import asyncio
from app.db.database import SessionLocal
from app.services.quickbooks_mcp import QuickBooksMCPSync

db = SessionLocal()
sync = QuickBooksMCPSync(db)
asyncio.run(sync.sync_all())
db.close()
EOF
```

## Troubleshooting

### "QB MCP server failed to connect"
```bash
# Check if QB MCP is installed
pip show quickbooks-mcp

# Try running MCP server directly
python -m quickbooks_mcp --version
```

### "QB API returned 403 Forbidden"
- Verify QB_REALM_ID is correct
- Verify QB_CLIENT_ID and QB_CLIENT_SECRET are correct
- Check Intuit Developer Portal app is in Production mode

### "Database connection failed"
```bash
psql -U bi_user -d bi_system -c "SELECT 1"
```

### "Scheduler not starting"
```bash
# Check if APScheduler is installed
pip show apscheduler

# Restart backend
pkill -f uvicorn
python -m uvicorn app.main:app --port 8000 &
sleep 5
tail -20 /var/log/blazebi/backend.log
```

## Summary

✅ **What was deployed:**
- QB MCP sync service (queries QB via MCP protocol)
- Daily scheduler job at 02:00 UTC
- QB query wrapper for Chat integration
- Settings UI updated (removed OAuth buttons)

✅ **What happens next:**
- Backend starts with scheduler
- QB sync runs daily at 02:00 UTC
- QB data synced to database tables
- Dashboard shows combined Zoho + QB metrics

✅ **No more QB OAuth:**
- No custom OAuth code to maintain
- No token refresh issues
- No 403/404 errors to debug
- MCP server handles authentication internally

## Questions?

Check logs: `tail -100 /var/log/blazebi/backend.log`
Check MCP docs: QB MCP GitHub repository
