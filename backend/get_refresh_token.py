#!/usr/bin/env python
"""Exchange authorization code for refresh token."""

import requests

code = '1000.020c4c31719823dd9d792207758d471b.cfcc433ae076a9bc2e0d81196e5df858'
client_id = '1000.NGAFZ94QUR61BKMWFGZCZ5THBXG9EZ'
client_secret = '228f0144667faadaaf29c0e884d2e8bd04714cb606'

url = 'https://accounts.zoho.in/oauth/v2/token'
params = {
    'code': code,
    'client_id': client_id,
    'client_secret': client_secret,
    'grant_type': 'authorization_code',
    'redirect_uri': 'http://localhost:8000/auth/callback',
}

print("[INFO] Requesting refresh token from Zoho...")
response = requests.post(url, params=params)
data = response.json()

if 'refresh_token' in data:
    print()
    print("=" * 70)
    print("[SUCCESS] Got new refresh token!")
    print("=" * 70)
    refresh_token = data.get("refresh_token")
    access_token = data.get("access_token")

    print(f"Refresh Token:\n  {refresh_token}")
    print()
    print(f"Access Token:\n  {access_token[:60]}...")
    print()
    print("=" * 70)
    print("Copy the Refresh Token above and send it to update .env")
    print("=" * 70)
else:
    print("[ERROR] Failed to get refresh token")
    print(f"Response: {data}")
