import httpx
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class ZohoAPIClient:
    """Zoho Books API client with OAuth2 support."""

    def __init__(self, api_key: Optional[str] = None):
        self.client_id = settings.zoho_client_id
        self.client_secret = settings.zoho_client_secret
        self.refresh_token = settings.zoho_refresh_token
        self.organization_id = settings.zoho_organization_id
        self.base_url = settings.zoho_api_base_url
        self.accounts_url = settings.zoho_accounts_url
        self.redirect_uri = settings.zoho_redirect_uri
        self.access_token: Optional[str] = None
        self.token_expiry: Optional[datetime] = None

        # Try to load tokens from database if not in settings
        if not self.refresh_token:
            self._load_tokens_from_db()

    def _load_tokens_from_db(self):
        """Load access and refresh tokens from database."""
        logger.info("Attempting to load OAuth tokens from database...")
        try:
            from app.db.database import SessionLocal
            from app.models.database import OAuthToken

            db = SessionLocal()
            oauth_token = db.query(OAuthToken).filter(OAuthToken.provider == "zoho").first()
            if oauth_token:
                self.refresh_token = oauth_token.refresh_token
                self.access_token = oauth_token.access_token
                # Set expiry to past so it gets refreshed on next API call
                self.token_expiry = datetime.utcnow() - timedelta(seconds=1)
                logger.info(f"Loaded tokens from database - Refresh: {self.refresh_token[:50]}..., Access: {self.access_token[:50]}...")
            else:
                logger.warning("No OAuth token found in database for provider 'zoho'")
            db.close()
        except Exception as e:
            logger.error(f"Failed to load tokens from database: {e}", exc_info=True)

    def get_access_token(self, authorization_code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token (OAuth callback)."""
        logger.info("Exchanging authorization code for access token")
        url = f"{self.accounts_url}/oauth/v2/token"

        payload = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "code": authorization_code,
        }

        try:
            response = httpx.post(url, data=payload, timeout=10)
            response.raise_for_status()

            data = response.json()
            self.access_token = data.get("access_token")
            self.refresh_token = data.get("refresh_token", self.refresh_token)
            expires_in = data.get("expires_in", 3600)
            self.token_expiry = datetime.utcnow() + timedelta(seconds=expires_in - 60)

            logger.info(f"Access token obtained, expires at {self.token_expiry}")
            return data
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to get access token: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error exchanging auth code: {e}")
            raise

    def _get_access_token(self) -> str:
        """Get a valid access token, refreshing if necessary."""
        logger.info(f"_get_access_token called: token={bool(self.access_token)}, expiry={self.token_expiry}, now={datetime.utcnow()}")

        if self.access_token and self.token_expiry and datetime.utcnow() < self.token_expiry:
            logger.info("Token is still valid, returning existing token")
            return self.access_token

        logger.info("Token expired or missing, refreshing Zoho access token")
        url = f"{self.accounts_url}/oauth/v2/token"

        payload = {
            "refresh_token": self.refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token",
        }

        logger.info(f"Token refresh request: {url}")
        logger.info(f"Refresh token: {self.refresh_token[:50]}...")

        try:
            response = httpx.post(url, data=payload, timeout=10)
            logger.info(f"Token refresh response status: {response.status_code}")
            logger.info(f"Token refresh response content: {response.text[:500]}")

            response.raise_for_status()

            data = response.json()
            self.access_token = data["access_token"]
            expires_in = data.get("expires_in", 3600)  # Default 1 hour
            self.token_expiry = datetime.utcnow() + timedelta(seconds=expires_in - 60)

            logger.info(f"Token refreshed successfully, expires at {self.token_expiry}")
            return self.access_token
        except Exception as e:
            logger.error(f"Token refresh failed: {e}", exc_info=True)
            raise
        return self.access_token

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        retries: int = 3,
    ) -> Dict[str, Any]:
        """Make authenticated API request to Zoho with retry logic."""
        url = f"{self.base_url}/books/v3{endpoint}"

        if params is None:
            params = {}

        headers = {
            "Authorization": f"Zoho-oauthtoken {self._get_access_token()}",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-com-zoho-books-organizationid": self.organization_id,
        }

        for attempt in range(retries):
            try:
                if method == "GET":
                    response = httpx.get(url, params=params, headers=headers, timeout=30, follow_redirects=False)
                elif method == "POST":
                    response = httpx.post(url, params=params, json=json_data, headers=headers, timeout=30, follow_redirects=False)
                elif method == "PUT":
                    response = httpx.put(url, params=params, json=json_data, headers=headers, timeout=30, follow_redirects=False)
                else:
                    raise ValueError(f"Unsupported method: {method}")

                if response.status_code == 302:
                    redirect_to = response.headers.get('location', 'unknown')
                    logger.error(f"HTTP 302 Redirect from {url} to {redirect_to}")
                    logger.error("LIKELY CAUSE: Zoho Books OAuth app does not have API access enabled. Please enable API access in Zoho Books settings.")
                    raise Exception(f"Zoho Books API authentication failed with 302 redirect. Enable API access in Zoho Books admin settings for this OAuth app.")

                response.raise_for_status()

                # Write all responses to file for debugging
                with open("C:\\Temp\\zoho_response_debug.txt", "a") as f:
                    f.write(f"\n{'='*80}\n")
                    f.write(f"Time: {__import__('datetime').datetime.utcnow()}\n")
                    f.write(f"Method: {method} {url}\n")
                    f.write(f"Status: {response.status_code}\n")
                    f.write(f"Content Length: {len(response.content)}\n")
                    if "location" in response.headers:
                        f.write(f"Location Header: {response.headers['location']}\n")
                    f.write(f"Content: {response.text[:1000]}\n")

                return response.json()

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 302:
                    logger.error(f"HTTP 302 Redirect: Zoho Books API is rejecting auth. Redirect to: {e.response.headers.get('location', 'N/A')}")
                    logger.error("This usually means: OAuth app lacks API access permission or token missing API scope")
                elif e.response.status_code == 401:
                    # Unauthorized, refresh token and retry
                    self.access_token = None
                    self.token_expiry = None
                    if attempt < retries - 1:
                        logger.warning("Got 401, refreshing token and retrying")
                        continue

                logger.error(f"HTTP {e.response.status_code}: {e.response.text[:500]}")
                raise

            except httpx.RequestError as e:
                if attempt < retries - 1:
                    logger.warning(f"Request error on attempt {attempt + 1}/{retries}: {e}")
                    continue
                raise

        raise Exception(f"Failed after {retries} retries")

    def get_records(
        self,
        resource: str,
        filters: Optional[List[tuple]] = None,
        sort_column: Optional[str] = None,
        sort_order: str = "A",
        page: int = 1,
        per_page: int = 100,
    ) -> List[Dict[str, Any]]:
        """Fetch records from Zoho (customers, invoices, products, payments)."""
        params = {
            "page": page,
            "per_page": per_page,
        }

        # Build filter string (Zoho uses custom filter syntax)
        if filters:
            filter_parts = []
            for field, operator, value in filters:
                if isinstance(value, datetime):
                    value = value.isoformat()
                filter_parts.append(f"{field}|{operator}|{value}")
            if filter_parts:
                params["filter_by"] = " AND ".join(filter_parts)

        logger.info(f"Fetching {resource} from Zoho with params: {params}")
        result = self._make_request("GET", f"/{resource}", params=params)

        return result.get(resource, [])

    def get_all_records(
        self,
        resource: str,
        filters: Optional[List[tuple]] = None,
    ) -> List[Dict[str, Any]]:
        """Fetch all records from Zoho, handling pagination."""
        all_records = []
        page = 1
        per_page = 100

        while True:
            records = self.get_records(
                resource=resource,
                filters=filters,
                page=page,
                per_page=per_page,
            )

            if not records:
                break

            all_records.extend(records)
            logger.info(f"Fetched page {page} of {resource}: {len(records)} records")

            if len(records) < per_page:
                break

            page += 1

        logger.info(f"Total {resource} fetched: {len(all_records)}")
        return all_records

    def get_customers(self, modified_since: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Fetch customers, optionally filtered by modified date."""
        filters = None
        if modified_since:
            filters = [("modified_time", ">=", modified_since)]
        return self.get_all_records("customers", filters=filters)

    def get_products(self, modified_since: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Fetch products, optionally filtered by modified date."""
        filters = None
        if modified_since:
            filters = [("modified_time", ">=", modified_since)]
        return self.get_all_records("items", filters=filters)

    def get_invoices(self, modified_since: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Fetch invoices, optionally filtered by modified date."""
        filters = None
        if modified_since:
            filters = [("modified_time", ">=", modified_since)]
        return self.get_all_records("invoices", filters=filters)

    def get_payments(self, modified_since: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Fetch payments, optionally filtered by modified date."""
        filters = None
        if modified_since:
            filters = [("modified_time", ">=", modified_since)]
        return self.get_all_records("payments", filters=filters)
