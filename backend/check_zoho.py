#!/usr/bin/env python
import sys
sys.path.insert(0, '.')
from app.config import get_settings

settings = get_settings()
print("ZOHO BOOKS API STATUS")
print("=" * 60)
print(f"Client ID:      {'SET' if settings.zoho_client_id else 'NOT SET'}")
print(f"Client Secret:  {'SET' if settings.zoho_client_secret else 'NOT SET'}")
print(f"Refresh Token:  {'SET' if settings.zoho_refresh_token else 'NOT SET'}")
print(f"Organization:   {'SET' if settings.zoho_organization_id else 'NOT SET'}")
print(f"API URL:        {settings.zoho_api_base_url}")
print("")

if settings.zoho_refresh_token:
    print("VERDICT: READY - Zoho Books API is configured")
    print("You can start syncing data from Zoho Books")
else:
    print("VERDICT: PENDING - OAuth authorization needed")
    print("Steps to complete OAuth:")
    print("  1. GET /api/auth/zoho/login")
    print("  2. User visits the returned auth_url")
    print("  3. User grants permission")
    print("  4. Zoho redirects to /api/auth/zoho/callback")
    print("  5. Token is saved")
