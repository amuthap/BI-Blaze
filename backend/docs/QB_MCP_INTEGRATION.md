# QuickBooks MCP Integration

This document describes the QuickBooks integration using the QuickBooks MCP (Model Context Protocol) server for scheduled data syncing.

## Architecture Overview

Instead of a custom OAuth implementation, we use the official QuickBooks MCP server which handles:
- OAuth authentication internally
- Token refresh and management
- Querying QB data via MCP protocol
- Preventing custom OAuth maintenance burden

## Setup Steps

### 1. Install QB MCP Server

The QB MCP server is a Python package that provides a MCP interface to QuickBooks data.

```bash
pip install quickbooks-mcp
```

### 2. Configure QB MCP Credentials

The MCP server requires QB OAuth credentials. These are configured via environment variables or a config file:

- `QB_CLIENT_ID` - Intuit OAuth app client ID
- `QB_CLIENT_SECRET` - Intuit OAuth app client secret
- `QB_REDIRECT_URI` - OAuth redirect URI (e.g., `https://yourdomain.com/oauth/callback`)
- `QB_REALM_ID` - The QB company/realm ID (obtained from first OAuth authorization)

### 3. MCP Server Startup

The MCP server can run as a separate process:

```bash
python -m quickbooks_mcp --port 3001
```

Or be integrated into the backend application via a subprocess.

## Scheduled Syncing

QB data is synced daily at 02:00 UTC via the scheduler in `app/jobs/scheduler.py`:

- **Job ID**: `qb_mcp_sync`
- **Schedule**: Daily at 02:00 UTC
- **Service**: `QuickBooksMCPSync` in `app/services/quickbooks_mcp.py`

### Data Synced

The following QB data is synced to the local database:

1. **Customers** → `QBCustomer` table
2. **Products/Items** → `QBProduct` table
3. **Invoices** → `QBInvoice` + `QBInvoiceLineItem` tables
4. **Payments** → `QBPayment` table

## Dashboard Integration

The dashboard aggregates data from both Zoho Books and QuickBooks:

- `DashboardService` queries both data sources
- Reports show unified metrics from both systems
- No user action required - synced data is automatically included

## Chat/Query Integration

For real-time QB queries through the Chat feature:

1. The Chat service can access QB data via the MCP server
2. MCP server handles QB API authentication internally
3. Queries run against real-time QB data

## Database Schema

QB-related tables in PostgreSQL:

```sql
CREATE TABLE qb_customer (
    id VARCHAR(255) PRIMARY KEY,
    display_name VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(20),
    billing_address JSONB,
    synced_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE qb_product (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255),
    description TEXT,
    unit_price DECIMAL(10, 2),
    synced_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE qb_invoice (
    id VARCHAR(255) PRIMARY KEY,
    customer_id VARCHAR(255),
    invoice_number VARCHAR(50),
    amount DECIMAL(10, 2),
    due_date DATE,
    status VARCHAR(50),
    synced_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE qb_payment (
    id VARCHAR(255) PRIMARY KEY,
    customer_id VARCHAR(255),
    amount DECIMAL(10, 2),
    payment_date DATE,
    synced_at TIMESTAMP DEFAULT NOW()
);
```

## Future Enhancements

1. **Real-time Sync**: Implement webhook-based sync for immediate data updates
2. **Error Handling**: Enhanced retry logic and error notifications
3. **MCP Chat Integration**: Full query support via Chat using MCP
4. **Multi-company Support**: Support multiple QB companies/realms
