#!/usr/bin/env python
"""Debug script to find correct Zoho Books API endpoint."""

import httpx
from app.services.zoho_api_client import ZohoAPIClient

print("=" * 70)
print("ZOHO BOOKS API ENDPOINT DEBUG")
print("=" * 70)

try:
    client = ZohoAPIClient()

    print("\n[STEP 1] Getting fresh access token...")
    token = client._get_access_token()
    print(f"[OK] Token obtained: {token[:50]}...")

    print("\n[STEP 2] Testing different endpoint formats...")
    print()

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    org_id = "60017561930"
    base_url = "https://www.zohoapis.in"

    # Test different endpoint formats
    endpoints_to_test = [
        f"{base_url}/books/api/v3/settings/organization?organization_id={org_id}",
        f"{base_url}/books/v3/settings/organization?organization_id={org_id}",
        f"{base_url}/books/api/v3/organizations?organization_id={org_id}",
        f"{base_url}/books/api/v3.1/customers?organization_id={org_id}",
        f"{base_url}/books/api/v2/customers?organization_id={org_id}",
        f"{base_url}/api/v3/books/settings/organization?organization_id={org_id}",
    ]

    for i, endpoint in enumerate(endpoints_to_test, 1):
        print(f"\nAttempt {i}: {endpoint}")
        try:
            response = httpx.get(endpoint, headers=headers, timeout=10, follow_redirects=True)
            print(f"  Status: {response.status_code}")

            if response.status_code == 200:
                print(f"  [SUCCESS] This endpoint works!")
                print(f"  Response: {response.json()}")
                print("\n" + "=" * 70)
                print(f"CORRECT ENDPOINT FOUND: {endpoint}")
                print("=" * 70)
                break
            else:
                try:
                    error_data = response.json()
                    print(f"  Error: {error_data.get('message', 'Unknown error')}")
                except:
                    print(f"  Response: {response.text[:200]}")
        except Exception as e:
            print(f"  Exception: {str(e)[:100]}")

    print("\n[STEP 3] Testing with actual /customers endpoint...")
    print()

    customer_endpoints = [
        f"{base_url}/books/api/v3/customers?page=1&per_page=5&organization_id={org_id}",
        f"{base_url}/books/api/v2/customers?page=1&per_page=5&organization_id={org_id}",
    ]

    for i, endpoint in enumerate(customer_endpoints, 1):
        print(f"\nCustomers Attempt {i}: {endpoint}")
        try:
            response = httpx.get(endpoint, headers=headers, timeout=10, follow_redirects=True)
            print(f"  Status: {response.status_code}")

            if response.status_code == 200:
                print(f"  [SUCCESS] Customers endpoint works!")
                data = response.json()
                print(f"  Response keys: {data.keys()}")
                print(f"  Sample: {str(data)[:300]}")
                print("\n" + "=" * 70)
                print(f"CUSTOMERS ENDPOINT WORKS: {endpoint}")
                print("=" * 70)
                break
            else:
                try:
                    error_data = response.json()
                    print(f"  Error: {error_data}")
                except:
                    print(f"  Response: {response.text[:200]}")
        except Exception as e:
            print(f"  Exception: {str(e)[:100]}")

except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("DEBUG COMPLETE")
print("=" * 70)
