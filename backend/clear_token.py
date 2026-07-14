#!/usr/bin/env python
"""Clear old OAuth token from database."""
from app.db.database import SessionLocal
from app.models.database import OAuthToken

db = SessionLocal()
old_token = db.query(OAuthToken).filter(OAuthToken.provider == "zoho").first()
if old_token:
    db.delete(old_token)
    db.commit()
    print("[OK] Old token deleted from database")
else:
    print("[INFO] No token found to delete")
db.close()
