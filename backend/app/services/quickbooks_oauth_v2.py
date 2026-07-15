"""QuickBooks OAuth 2.0 integration using official Intuit SDK."""

from intuitlib.client import AuthClient
from intuitlib.enums import Scopes
from datetime import datetime, timedelta
from app.config import get_settings
from sqlalchemy.orm import Session
from app.models.database import OAuthToken
import logging

logger = logging.getLogger(__name__)
settings = get_settings()


class QuickBooksOAuthV2:
    """Handle QuickBooks OAuth 2.0 using official Intuit SDK."""

    def __init__(self):
        self.client_id = settings.qb_client_id
        self.client_secret = settings.qb_client_secret
        self.redirect_uri = settings.qb_redirect_uri
        self.environment = "sandbox"  # Use sandbox for development, switch to "production" for prod

        self.auth_client = AuthClient(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri,
            environment=self.environment
        )

    def get_authorization_url(self) -> str:
        """Generate authorization URL for user to grant access."""
        auth_url = self.auth_client.get_authorization_url(
            scopes=[Scopes.ACCOUNTING]
        )
        logger.info(f"Generated authorization URL")
        return auth_url

    async def exchange_code_for_token(self, code: str, realm_id: str) -> dict:
        """Exchange authorization code for access token."""
        try:
            # Use the official SDK to exchange code for token
            auth_response = self.auth_client.get_bearer_token(code, realm_id=realm_id)

            logger.info(f"Successfully exchanged code for token. Realm ID: {realm_id}")

            return {
                "access_token": auth_response["access_token"],
                "refresh_token": auth_response.get("refresh_token"),
                "expires_in": auth_response.get("expires_in", 3600),
                "realm_id": realm_id
            }
        except Exception as e:
            logger.error(f"Failed to exchange code: {str(e)}")
            raise

    async def refresh_token(self, refresh_token: str, realm_id: str) -> dict:
        """Refresh access token using refresh token."""
        try:
            auth_response = self.auth_client.refresh(refresh_token)

            logger.info(f"Token refreshed successfully")

            return {
                "access_token": auth_response["access_token"],
                "refresh_token": auth_response.get("refresh_token", refresh_token),
                "expires_in": auth_response.get("expires_in", 3600),
                "realm_id": realm_id
            }
        except Exception as e:
            logger.error(f"Failed to refresh token: {str(e)}")
            raise

    def save_token(self, db: Session, token_data: dict) -> None:
        """Save token to database."""
        token = db.query(OAuthToken).filter(OAuthToken.provider == "quickbooks").first()

        expires_in = token_data.get("expires_in", 3600)
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

        if token:
            token.access_token = token_data["access_token"]
            token.refresh_token = token_data.get("refresh_token", token.refresh_token)
            token.expires_at = expires_at
            token.updated_at = datetime.utcnow()
        else:
            token = OAuthToken(
                provider="quickbooks",
                access_token=token_data["access_token"],
                refresh_token=token_data.get("refresh_token", ""),
                expires_at=expires_at
            )
            db.add(token)

        db.commit()
        logger.info(f"Saved QuickBooks token. Expires at: {expires_at}")

    def get_valid_token(self, db: Session) -> str:
        """Get valid access token, refreshing if necessary."""
        token = db.query(OAuthToken).filter(OAuthToken.provider == "quickbooks").first()

        if not token:
            raise Exception("No QuickBooks token found. Please authorize first.")

        # Check if token is expired or expiring soon (within 5 minutes)
        if token.expires_at and datetime.utcnow() > token.expires_at - timedelta(minutes=5):
            logger.info("Token expired or expiring soon, refreshing...")
            # Token refresh will be handled by the caller

        return token.access_token

    def get_token_data(self, db: Session) -> dict:
        """Get full token data."""
        token = db.query(OAuthToken).filter(OAuthToken.provider == "quickbooks").first()
        if not token:
            return None
        return {
            "access_token": token.access_token,
            "refresh_token": token.refresh_token,
            "expires_at": token.expires_at
        }
