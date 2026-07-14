#!/usr/bin/env python
"""Test Zoho API access directly with current token."""

from app.services.zoho_api_client import ZohoAPIClient
import json

print("=" * 70)
print("CHECKING ZOHO ACCOUNT AND API ACCESS")
print("=" * 70)

try:
    client = ZohoAPIClient()
    token = client._get_access_token()

    print(f"\n[INFO] Refresh Token: {client.refresh_token[:50]}...")
    print(f"[INFO] Organization ID: {client.organization_id}")
    print(f"[INFO] API Base URL: {client.base_url}")
    print(f"[INFO] Access Token obtained successfully")

    print("\n" + "=" * 70)
    print("VERIFICATION STEPS:")
    print("=" * 70)
    print("""
1. Go to Zoho Books: https://books.zoho.in/
2. Navigate to Settings (Gear Icon)
3. Check:
   - API is ENABLED (Settings > API)
   - Your subscription includes API access
   - OAuth app has proper permissions

4. If API is disabled, click "ENABLE" to activate it

5. After enabling, come back here and we'll test again

Alternatively, contact Zoho support if API access is restricted
    """)

    print("=" * 70)
    print("[NEXT STEP] Reply with screenshot of your API settings")
    print("=" * 70)

except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()
