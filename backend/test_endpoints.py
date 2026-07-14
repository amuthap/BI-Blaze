#!/usr/bin/env python
"""Test different Books API endpoint formats."""
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
print(f"Testing with access token: {access_token[:50]}...\n")

# Test different endpoint formats
endpoints = [
    ("books.zoho.in (current)", "https://books.zoho.in/books/api/v3/customers"),
    ("zoho.in variant", "https://zoho.in/books/api/v3/customers"),
    ("api.zoho.in variant", "https://api.zoho.in/books/api/v3/customers"),
]

headers = {
    "Authorization": f"Zoho-oauthtoken {access_token}",
    "Accept": "application/json",
    "Content-Type": "application/json",
}
params = {
    "organization_id": settings.zoho_organization_id,
    "page": 1,
    "per_page": 1,
}

for name, url in endpoints:
    print(f"Testing: {name}")
    print(f"URL: {url}")
    try:
        response = httpx.get(url, params=params, headers=headers, timeout=10, follow_redirects=False)
        print(f"Status: {response.status_code}")

        if response.status_code == 302:
            print(f"Redirect: {response.headers.get('location')}")
        elif response.status_code == 200:
            try:
                data = response.json()
                print(f"SUCCESS! Got JSON - Keys: {list(data.keys())}")
            except:
                print(f"Got 200 but not JSON")
        else:
            print(f"Response: {response.text[:200]}")
    except Exception as e:
        print(f"Error: {e}")
    print()

db.close()
