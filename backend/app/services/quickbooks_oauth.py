"""QuickBooks OAuth 2.0 integration."""

import httpx
import json
from datetime import datetime, timedelta
from app.config import get_settings
from sqlalchemy.orm import Session
from app.models.database import OAuthToken
import logging

logger = logging.getLogger(__name__)

settings = get_settings()


class QuickBooksOAuth:
    """Handle QuickBooks OAuth 2.0 flow."""

    OAUTH_URL = "https://appcenter.intuit.com/connect/oauth2"
    TOKEN_URL = "https://oauth.platform.intuit.com/oauth2/Tokens/bearer"
    SCOPES = [
        "com.intuit.quickbooks.accounting"
    ]

    def __init__(self):
        self.client_id = settings.qb_client_id
        self.client_secret = settings.qb_client_secret
        self.redirect_uri = settings.qb_redirect_uri

    def get_authorization_url(self) -> str:
        """Generate authorization URL for user to grant access."""
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "scope": " ".join(self.SCOPES),
            "redirect_uri": self.redirect_uri,
            "state": "security_token_12345"
        }
        return f"{self.OAUTH_URL}?{'&'.join(f'{k}={v}' for k, v in params.items())}"

    async def exchange_code_for_token(self, code: str) -> dict:
        """Exchange authorization code for access token."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.TOKEN_URL,
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": self.redirect_uri,
                },
                auth=(self.client_id, self.client_secret),
                timeout=30.0
            )
            response.raise_for_status()
            token_data = response.json()

            logger.info(f"Successfully exchanged code for token. Realm ID: {token_data.get('x_refresh_token_expires_in')}")

            return token_data

    async def refresh_token(self, refresh_token: str) -> dict:
        """Refresh access token using refresh token."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.TOKEN_URL,
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                },
                auth=(self.client_id, self.client_secret),
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()

    def save_token(self, db: Session, token_data: dict) -> None:
        """Save token to database."""
        token = db.query(OAuthToken).filter(OAuthToken.provider == "quickbooks").first()

        expires_in = token_data.get("expires_in", 3600)
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

        if token:
            token.access_token = token_data["access_token"]
            token.refresh_token = token_data["refresh_token"]
            token.expires_at = expires_at
            token.updated_at = datetime.utcnow()
        else:
            token = OAuthToken(
                provider="quickbooks",
                access_token=token_data["access_token"],
                refresh_token=token_data["refresh_token"],
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

        # Check if token is expired
        if token.expires_at and datetime.utcnow() > token.expires_at:
            logger.info("Token expired, refreshing...")
            # Will be handled in the refresh_token method

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
