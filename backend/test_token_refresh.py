#!/usr/bin/env python
"""Test token refresh directly."""
import sys
sys.path.insert(0, '.')

from app.services.zoho_api_client import ZohoAPIClient
from app.db.database import SessionLocal
from app.models.database import OAuthToken

# Get token from database
db = SessionLocal()
oauth_token = db.query(OAuthToken).filter(OAuthToken.provider == "zoho").first()

print(f"[TEST] Token in DB: {oauth_token.refresh_token[:50]}...")

# Create client - this will load tokens from DB
client = ZohoAPIClient()
print(f"[TEST] Client loaded - access_token: {bool(client.access_token)}")
print(f"[TEST] Token expiry: {client.token_expiry}")

# Call _get_access_token() which should trigger refresh
print(f"\n[TEST] Calling _get_access_token()...")
try:
    token = client._get_access_token()
    print(f"[OK] Got token: {token[:50]}...")
    print(f"[OK] Token expiry after refresh: {client.token_expiry}")
except Exception as e:
    print(f"[ERROR] {e}")

db.close()
