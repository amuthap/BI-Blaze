#!/usr/bin/env python
"""Test Zoho Books API directly with the new token."""
import httpx
from app.db.database import SessionLocal
from app.models.database import OAuthToken
from app.config import get_settings

settings = get_settings()
db = SessionLocal()

token_record = db.query(OAuthToken).filter(OAuthToken.provider == "zoho").first()
if not token_record:
    print("[ERROR] No token in database")
    exit(1)

access_token = token_record.access_token
print(f"Testing with access token: {access_token[:50]}...")

# Test the API call
url = f"{settings.zoho_api_base_url}/books/api/v3/customers"
headers = {
    "Authorization": f"Zoho-oauthtoken {access_token}",
    "Accept": "application/json",
    "Content-Type": "application/json",
}
params = {
    "organization_id": settings.zoho_organization_id,
    "page": 1,
    "per_page": 10,
}

print(f"\nURL: {url}")
print(f"Headers: {headers}")
print(f"Params: {params}")

response = httpx.get(url, params=params, headers=headers, timeout=10, follow_redirects=False)
print(f"\nStatus: {response.status_code}")
print(f"Headers: {dict(response.headers)}")

if response.status_code == 302:
    print(f"Redirect Location: {response.headers.get('location')}")
    print("\nAPI is rejecting the authentication.")
    print("Possible causes:")
    print("1. OAuth app doesn't have 'Zoho Books API' enabled as an associated product")
    print("2. Account-level API permissions need to be granted")
    print("3. Different API endpoint or domain may be required")
elif response.status_code == 200:
    try:
        data = response.json()
        print(f"SUCCESS! Got JSON response")
        print(f"Keys: {list(data.keys())}")
    except:
        print(f"Status 200 but response is not JSON")
        print(f"Content: {response.text[:500]}")
else:
    print(f"Status: {response.status_code}")
    print(f"Content: {response.text[:500]}")

db.close()
