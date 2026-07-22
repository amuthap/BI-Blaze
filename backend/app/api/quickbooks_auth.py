"""QuickBooks OAuth endpoints for initial credential setup."""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import logging

from app.config import get_settings
from app.db.database import get_db
from app.models.database import OAuthToken

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth/quickbooks", tags=["quickbooks"])

settings = get_settings()


@router.get("/authorize")
async def authorize_quickbooks():
    """Redirect to QuickBooks OAuth authorization."""
    try:
        from intuitlib.client import AuthClient
        from intuitlib.enums import Scopes

        auth_client = AuthClient(
            client_id=settings.qb_client_id,
            client_secret=settings.qb_client_secret,
            redirect_uri=settings.qb_redirect_uri,
            environment="production"
        )

        auth_url = auth_client.get_authorization_url(
            scopes=[Scopes.ACCOUNTING, Scopes.PAYMENT]
        )

        logger.info(f"Redirecting to QB authorization: {auth_url[:80]}...")
        return RedirectResponse(url=auth_url, status_code=302)

    except Exception as e:
        logger.error(f"Failed to get QB authorization URL: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/callback")
async def quickbooks_callback(
    code: str = None,
    realmId: str = None,
    state: str = None,
    db: Session = Depends(get_db),
):
    """Handle QuickBooks OAuth callback."""
    try:
        if not code or not realmId:
            raise ValueError("Missing code or realmId from QB callback")

        from intuitlib.client import AuthClient

        logger.info(f"QB OAuth callback received - exchanging code for token (realm: {realmId})")

        auth_client = AuthClient(
            client_id=settings.qb_client_id,
            client_secret=settings.qb_client_secret,
            redirect_uri=settings.qb_redirect_uri,
            environment="production"
        )

        # Exchange code for tokens
        tokens = auth_client.get_bearer_token(code)

        logger.info(f"Successfully exchanged code for tokens")

        # Save tokens to database
        oauth_token = db.query(OAuthToken).filter(
            OAuthToken.provider == "quickbooks"
        ).first()

        if not oauth_token:
            oauth_token = OAuthToken(provider="quickbooks")

        oauth_token.access_token = tokens.get("access_token", "")
        oauth_token.refresh_token = tokens.get("refresh_token", "")
        oauth_token.realm_id = realmId
        oauth_token.expires_at = tokens.get("x_refresh_token_expires_in")

        db.add(oauth_token)
        db.commit()

        logger.info(f"✅ QB OAuth tokens saved - Realm ID: {realmId}")

        # Redirect to settings page showing success and credentials
        return RedirectResponse(
            url=f"https://blazebi.hyperbig.com/settings?qb=success&realm_id={realmId}&refresh_token={tokens.get('refresh_token', '')[:20]}...",
            status_code=302
        )

    except Exception as e:
        logger.error(f"QB OAuth callback failed: {e}")
        return RedirectResponse(
            url=f"https://blazebi.hyperbig.com/settings?qb=error&error={str(e)[:50]}",
            status_code=302
        )


@router.get("/status")
async def get_quickbooks_status(db: Session = Depends(get_db)):
    """Get QB connection status."""
    try:
        token = db.query(OAuthToken).filter(
            OAuthToken.provider == "quickbooks"
        ).first()

        if not token or not token.realm_id:
            return {
                "connected": False,
                "realm_id": None,
                "message": "Not connected - Click to authorize"
            }

        return {
            "connected": True,
            "realm_id": token.realm_id,
            "message": f"Connected - Realm ID: {token.realm_id}"
        }

    except Exception as e:
        logger.error(f"Failed to get QB status: {e}")
        return {
            "connected": False,
            "error": str(e)
        }
