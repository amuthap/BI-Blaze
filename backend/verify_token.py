from app.db.database import SessionLocal
from app.models.database import OAuthToken

db = SessionLocal()
token = db.query(OAuthToken).filter(OAuthToken.provider == "zoho").first()
if token:
    print(f"[OK] Token saved in database")
    print(f"    Refresh: {token.refresh_token[:50]}...")
    print(f"    Access: {token.access_token[:50]}...")
else:
    print("[ERROR] Token not found in database")
db.close()
