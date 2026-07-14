import sys
sys.path.insert(0, '.')

from app.config import get_settings
from app.services.zoho_api_client import ZohoAPIClient

settings = get_settings()
print("Zoho Configuration:")
print(f"  Client ID: {settings.zoho_client_id[:20]}...")
print(f"  Client Secret: {settings.zoho_client_secret[:20] if settings.zoho_client_secret else 'NOT SET'}...")
print(f"  Refresh Token: {settings.zoho_refresh_token if settings.zoho_refresh_token else 'NOT SET'}")
print(f"  Organization ID: {settings.zoho_organization_id}")
print(f"  API Base URL: {settings.zoho_api_base_url}")
print(f"  Accounts URL: {settings.zoho_accounts_url}")
print("")

# Try to initialize the client
try:
    client = ZohoAPIClient()
    print("✅ ZohoAPIClient initialized successfully")
    print(f"  Access Token: {client.access_token if client.access_token else 'Not yet obtained'}")
    print(f"  Refresh Token: {client.refresh_token if client.refresh_token else 'Not set'}")
except Exception as e:
    print(f"❌ Error initializing ZohoAPIClient: {e}")
    import traceback
    traceback.print_exc()
