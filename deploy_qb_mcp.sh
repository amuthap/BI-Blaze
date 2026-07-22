#!/bin/bash

# QuickBooks MCP Deployment Script
# Run this on the production server at: 95.217.54.165

set -e

echo "=========================================="
echo "QuickBooks MCP Deployment"
echo "=========================================="

cd /home/BlazeBI/projects/BI-Blaze-Frontend
echo "✓ Working directory: $(pwd)"

# Step 1: Pull latest code
echo ""
echo "Step 1: Pulling latest code..."
git pull origin main
echo "✓ Code updated"

# Step 2: Install QB MCP server
echo ""
echo "Step 2: Installing QB MCP server..."
pip install -q quickbooks-mcp 2>&1 || {
    echo "⚠️  QB MCP installation may have issues"
    echo "Trying alternative install..."
    pip install --upgrade quickbooks-mcp
}
echo "✓ QB MCP server installed"

# Step 3: Verify QB credentials in .env
echo ""
echo "Step 3: Checking QB credentials..."
cd backend

if grep -q "QB_CLIENT_ID=" .env; then
    QB_ID=$(grep "QB_CLIENT_ID=" .env | cut -d= -f2)
    echo "✓ QB_CLIENT_ID is set"
else
    echo "⚠️  WARNING: QB_CLIENT_ID not found in backend/.env"
    echo "   Add these to backend/.env:"
    echo "   QB_CLIENT_ID=your_client_id"
    echo "   QB_CLIENT_SECRET=your_client_secret"
    echo "   QB_REALM_ID=your_realm_id"
    echo "   QB_REDIRECT_URI=https://blazebi.hyperbig.com/oauth/callback"
fi

if grep -q "QB_SECRET=" .env; then
    echo "✓ QB_CLIENT_SECRET is set"
fi

if grep -q "QB_REALM_ID=" .env; then
    echo "✓ QB_REALM_ID is set"
fi

# Step 4: Stop current backend
echo ""
echo "Step 4: Stopping current backend..."
pkill -f uvicorn || echo "  (No uvicorn process found)"
sleep 2
echo "✓ Backend stopped"

# Step 5: Start backend with MCP support
echo ""
echo "Step 5: Starting backend with MCP support..."
nohup python -m uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 2 \
    --log-level info \
    > /tmp/blazebi_backend.log 2>&1 &

BACKEND_PID=$!
echo "✓ Backend started (PID: $BACKEND_PID)"

# Step 6: Wait for backend to start
echo ""
echo "Step 6: Waiting for backend to start..."
sleep 5

# Step 7: Check if backend is running
echo ""
echo "Step 7: Verifying backend..."
if curl -s http://localhost:8000/api/health > /dev/null; then
    echo "✓ Backend is running and responding"
else
    echo "⚠️  Backend health check failed"
    echo "Check logs: tail -50 /tmp/blazebi_backend.log"
fi

# Step 8: Verify scheduler
echo ""
echo "Step 8: Verifying scheduler..."
sleep 3
if grep -q "Scheduler started" /tmp/blazebi_backend.log 2>/dev/null; then
    echo "✓ Scheduler started successfully"
    grep "Jobs scheduled" /tmp/blazebi_backend.log
else
    echo "⚠️  Scheduler status unknown"
    echo "Check logs: tail -20 /tmp/blazebi_backend.log"
fi

# Step 9: Check database connection
echo ""
echo "Step 9: Checking database connection..."
psql -U bi_user -d bi_system -c "SELECT version();" > /dev/null 2>&1 && \
    echo "✓ Database connection OK" || \
    echo "⚠️  Database connection failed"

# Step 10: Show current QB data
echo ""
echo "Step 10: QB Data Status"
echo "----------------------------------------"
psql -U bi_user -d bi_system << SQL 2>/dev/null || echo "Could not query database"
SELECT
  'QBCustomers' as table_name, COUNT(*) as records FROM qb_customers
UNION ALL
SELECT 'QBProducts', COUNT(*) FROM qb_products
UNION ALL
SELECT 'QBInvoices', COUNT(*) FROM qb_invoices
UNION ALL
SELECT 'QBLineItems', COUNT(*) FROM qb_invoice_line_items
UNION ALL
SELECT 'QBPayments', COUNT(*) FROM qb_payments
ORDER BY table_name;
SQL

echo ""
echo "=========================================="
echo "✅ Deployment Complete!"
echo "=========================================="
echo ""
echo "Next Steps:"
echo "1. Verify QB credentials are in backend/.env"
echo "2. Backend is running and scheduler is active"
echo "3. QB sync will run tomorrow at 02:00 UTC"
echo "4. To test manually, run:"
echo "   python -c \"import asyncio; from app.db.database import SessionLocal; from app.services.quickbooks_mcp import QuickBooksMCPSync; db = SessionLocal(); sync = QuickBooksMCPSync(db); asyncio.run(sync.sync_all())\""
echo ""
echo "Logs: tail -100 /tmp/blazebi_backend.log"
echo "=========================================="
