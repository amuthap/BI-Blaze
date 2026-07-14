#!/usr/bin/env python
"""Test if the saved Zoho tokens are valid."""
import sys
sys.path.insert(0, '.')

from app.db.database import SessionLocal
from app.models.database import OAuthToken
import httpx
from app.config import get_settings

settings = get_settings()
db = SessionLocal()

# Get token from database
oauth_token = db.query(OAuthToken).filter(OAuthToken.provider == "zoho").first()
if not oauth_token:
    print("[FAILED] No token in database")
    sys.exit(1)

access_token = oauth_token.access_token
refresh_token = oauth_token.refresh_token

print(f"[INFO] Access Token: {access_token[:50]}...")
print(f"[INFO] Refresh Token: {refresh_token[:50]}...")

# Test 1: Try to refresh the token
print("\n[TEST 1] Attempting to refresh access token...")
refresh_url = f"{settings.zoho_accounts_url}/oauth/v2/token"
refresh_payload = {
    "refresh_token": refresh_token,
    "client_id": settings.zoho_client_id,
    "client_secret": settings.zoho_client_secret,
    "grant_type": "refresh_token",
}

try:
    response = httpx.post(refresh_url, data=refresh_payload, timeout=10)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:500]}")

    if response.status_code == 200:
        data = response.json()
        new_access_token = data.get("access_token")
        print(f"[OK] New access token: {new_access_token[:50]}...")
    else:
        print(f"[FAILED] Token refresh failed")
        sys.exit(1)
except Exception as e:
    print(f"[ERROR] {e}")
    sys.exit(1)

# Test 2: Try API call with new token
print("\n[TEST 2] Testing API call with new access token...")
api_url = f"{settings.zoho_api_base_url}/books/api/v3/customers"
headers = {
    "Authorization": f"Zoho-oauthtoken {new_access_token}",
    "Accept": "application/json",
    "Content-Type": "application/json",
}
params = {
    "organization_id": settings.zoho_organization_id,
}

try:
    response = httpx.get(api_url, params=params, headers=headers, timeout=10)
    print(f"Status: {response.status_code}")
    print(f"Content-Length: {len(response.content)}")

    if response.status_code == 200:
        try:
            data = response.json()
            print(f"[OK] Got JSON response!")
            print(f"Keys: {list(data.keys())}")
            customer_count = len(data.get('customers', []))
            print(f"[OK] Customers in response: {customer_count}")
        except Exception as e:
            print(f"[FAILED] Response is not JSON: {e}")
            print(f"First 500 chars: {response.text[:500]}")
    else:
        print(f"[FAILED] HTTP {response.status_code}")
except Exception as e:
    print(f"[ERROR] {e}")
    sys.exit(1)

db.close()
print("\n[DONE] Token test complete")
