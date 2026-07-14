#!/usr/bin/env python
"""Direct token save script - paste your refresh token here."""
import sys
sys.path.insert(0, '.')

from app.db.database import SessionLocal
from app.models.database import OAuthToken
from datetime import datetime, timedelta

# PASTE YOUR REFRESH TOKEN HERE
refresh_token = input("Paste your Zoho refresh token: ").strip()
access_token = input("Paste your Zoho access token: ").strip()

if not refresh_token or not access_token:
    print("Error: Both tokens required")
    sys.exit(1)

db = SessionLocal()

# Delete old token
old = db.query(OAuthToken).filter(OAuthToken.provider == "zoho").first()
if old:
    db.delete(old)
    db.commit()

# Save new token
token = OAuthToken(
    provider="zoho",
    access_token=access_token,
    refresh_token=refresh_token,
    expires_at=datetime.utcnow() + timedelta(hours=1)
)
db.add(token)
db.commit()

print(f"\n[OK] Token saved successfully!")
print(f"Refresh token: {refresh_token[:50]}...")

db.close()
