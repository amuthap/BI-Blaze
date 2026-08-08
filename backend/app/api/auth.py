"""OAuth authentication endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import logging

from app.config import get_settings
from app.db.database import get_db
from app.services.zoho_api_client import ZohoAPIClient

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["auth"])

settings = get_settings()


@router.get("/zoho/login")
async def zoho_login():
    """Redirect user to Zoho Books OAuth login."""
    auth_url = (
        f"{settings.zoho_accounts_url}/oauth/v2/auth"
        f"?client_id={settings.zoho_client_id}"
        f"&redirect_uri={settings.zoho_redirect_uri}"
        f"&response_type=code"
        f"&scope=ZohoBooks.invoices.ALL,ZohoBooks.customers.ALL,ZohoBooks.items.ALL,ZohoBooks.payments.ALL,ZohoBooks.settings.READ"
        f"&access_type=offline"
        f"&prompt=consent"
        f"&state=security_token"
    )
    return {"auth_url": auth_url}


@router.get("/callback")
async def callback(
    code: str = Query(...),
    state: str = Query(None),
    db: Session = Depends(get_db),
):
    """Handle OAuth callback (simple redirect)."""
    return await zoho_callback(code=code, state=state, db=db)


@router.get("/zoho/callback")
async def zoho_callback(
    code: str = Query(...),
    state: str = Query(None),
    db: Session = Depends(get_db),
):
    """Handle Zoho OAuth callback and exchange code for token."""
    try:
        if not code:
            raise HTTPException(status_code=400, detail="Authorization code missing")

        logger.info("Received Zoho OAuth callback")

        # Write debug log file
        debug_log = "C:\\Temp\\zoho_auth_debug.log"
        import os
        os.makedirs("C:\\Temp", exist_ok=True)
        with open(debug_log, "a") as f:
            f.write(f"\n=== OAuth Callback Debug ===\n")
            f.write(f"Code: {code[:50]}\n")

        # Exchange code for token
        client = ZohoAPIClient(api_key=settings.anthropic_api_key)
        token_data = client.get_access_token(code)

        logger.info(f"Full token_data: {token_data}")
        with open(debug_log, "a") as f:
            f.write(f"Token data keys: {list(token_data.keys())}\n")
            f.write(f"Token data: {token_data}\n")

        if not token_data or "access_token" not in token_data:
            logger.error(f"Failed to get access token: {token_data}")
            raise HTTPException(status_code=400, detail="Failed to obtain access token")

        # Store tokens in database
        from app.models.database import SyncHistory, SyncStatusEnum, SyncTypeEnum, OAuthToken
        from datetime import datetime, timedelta

        access_token = token_data.get("access_token", "")
        refresh_token = token_data.get("refresh_token", "")
        expires_in = token_data.get("expires_in", 3600)

        logger.info(f"Token data received with keys: {list(token_data.keys())}")
        logger.info(f"Access Token: {access_token[:50]}...")
        logger.info(f"Refresh Token: {refresh_token[:50] if refresh_token else 'EMPTY'}...")

        if not refresh_token:
            logger.error("Refresh token is empty in OAuth response!")
            raise HTTPException(status_code=400, detail="Refresh token not provided in OAuth response")

        # Write tokens to file for debugging/persistence
        import os
        os.makedirs("C:\\Temp", exist_ok=True)
        with open("C:\\Temp\\zoho_tokens.txt", "w") as f:
            f.write(f"access_token={access_token}\n")
            f.write(f"refresh_token={refresh_token}\n")
            f.write(f"expires_in={expires_in}\n")
        logger.info("Tokens written to C:\\Temp\\zoho_tokens.txt")

        # Save or update OAuth token in database
        try:
            logger.info("Querying existing OAuth token...")
            oauth_token = db.query(OAuthToken).filter(OAuthToken.provider == "zoho").first()

            if oauth_token:
                logger.info("Updating existing OAuth token")
                oauth_token.access_token = access_token
                oauth_token.refresh_token = refresh_token
                oauth_token.expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
                oauth_token.updated_at = datetime.utcnow()
            else:
                logger.info("Creating new OAuth token record")
                oauth_token = OAuthToken(
                    provider="zoho",
                    access_token=access_token,
                    refresh_token=refresh_token,
                    expires_at=datetime.utcnow() + timedelta(seconds=expires_in)
                )
                db.add(oauth_token)

            sync_record = SyncHistory(
                entity_type="auth",
                sync_type=SyncTypeEnum.full,
                status=SyncStatusEnum.completed,
                records_synced=1,
                error_message=None
            )
            db.add(sync_record)

            logger.info("Committing database changes...")
            db.commit()
            logger.info("OAuth tokens saved successfully to database")
        except Exception as e:
            logger.error(f"Failed to save to database: {e}", exc_info=True)
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to save tokens: {e}")
        logger.info("IMPORTANT: The refresh token has been saved. Zoho Books API is now ACTIVE!")

        # Redirect to frontend with success
        return {
            "status": "success",
            "message": "OAuth authentication successful! Copy the tokens below if auto-save failed.",
            "access_token": token_data.get("access_token"),
            "refresh_token": refresh_token,
            "next_url": "http://localhost:3000/home",
        }

    except Exception as e:
        logger.error(f"OAuth callback error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/zoho/status")
async def zoho_status(db: Session = Depends(get_db)):
    """Check if Zoho Books API is authenticated."""
    from app.models.database import SyncHistory, SyncStatusEnum

    try:
        # Check for recent successful auth
        latest_auth = (
            db.query(SyncHistory)
            .filter(SyncHistory.entity_type == "auth")
            .order_by(SyncHistory.started_at.desc())
            .first()
        )

        if latest_auth and latest_auth.status == SyncStatusEnum.completed:
            return {
                "authenticated": True,
                "last_auth": str(latest_auth.started_at),
                "message": "Zoho Books API is authenticated",
            }
        else:
            return {
                "authenticated": False,
                "message": "Please authenticate with Zoho Books",
                "login_url": "/api/auth/zoho/login",
            }
    except Exception as e:
        logger.error(f"Error checking status: {e}")
        return {
            "authenticated": False,
            "message": "Error checking authentication status",
            "error": str(e),
        }


@router.get("/quickbooks/login")
async def quickbooks_login():
    """Redirect user to QuickBooks OAuth login."""
    from urllib.parse import quote, urlencode
    from starlette.responses import RedirectResponse

    # Use final Intuit endpoint (they redirect /connect/oauth2 → /app/connect/oauth2)
    params = {
        "client_id": settings.qb_client_id,
        "response_type": "code",
        "scope": "com.intuit.quickbooks.accounting",
        "redirect_uri": settings.qb_redirect_uri,
        "state": "security_token"
    }

    # Build URL with proper encoding (no HTML entities)
    auth_url = "https://appcenter.intuit.com/app/connect/oauth2?" + urlencode(params)

    # Return raw redirect response (avoids any HTML escaping)
    response = RedirectResponse(url=auth_url, status_code=302)
    return response


@router.get("/quickbooks/callback")
async def quickbooks_callback(
    code: str = Query(...),
    state: str = Query(None),
    realmId: str = Query(None),
    db: Session = Depends(get_db),
):
    """Handle QuickBooks OAuth callback and exchange code for token."""
    try:
        if not code:
            raise HTTPException(status_code=400, detail="Authorization code missing")

        if not realmId:
            raise HTTPException(status_code=400, detail="Realm ID missing")

        logger.info(f"Received QB OAuth callback for realm {realmId}")

        # Exchange code for token
        import base64
        import requests

        token_url = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"

        credentials = f"{settings.qb_client_id}:{settings.qb_client_secret}"
        encoded = base64.b64encode(credentials.encode()).decode()

        headers = {
            "Authorization": f"Basic {encoded}",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": settings.qb_redirect_uri
        }

        response = requests.post(token_url, headers=headers, data=data)
        response.raise_for_status()

        token_data = response.json()

        logger.info(f"QB tokens received: {list(token_data.keys())}")

        # Extract tokens
        access_token = token_data.get("access_token", "")
        refresh_token = token_data.get("refresh_token", "")
        expires_in = token_data.get("expires_in", 3600)

        if not access_token or not refresh_token:
            logger.error(f"Missing tokens in QB response: {token_data}")
            raise HTTPException(status_code=400, detail="Failed to obtain tokens from QuickBooks")

        # Save OAuth token in database
        from app.models.database import OAuthToken
        from datetime import datetime, timedelta

        try:
            oauth_token = db.query(OAuthToken).filter(
                OAuthToken.provider == "quickbooks"
            ).first()

            if oauth_token:
                logger.info("Updating existing QB OAuth token")
                oauth_token.access_token = access_token
                oauth_token.refresh_token = refresh_token
                oauth_token.expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
                oauth_token.updated_at = datetime.utcnow()
            else:
                logger.info("Creating new QB OAuth token record")
                oauth_token = OAuthToken(
                    provider="quickbooks",
                    access_token=access_token,
                    refresh_token=refresh_token,
                    expires_at=datetime.utcnow() + timedelta(seconds=expires_in)
                )
                db.add(oauth_token)

            # Save realm_id to a config file or return it to the user
            from app.models.database import SyncHistory, SyncTypeEnum, SyncStatusEnum
            sync_record = SyncHistory(
                entity_type="quickbooks_auth",
                sync_type=SyncTypeEnum.full,
                status=SyncStatusEnum.completed,
                records_synced=1,
                error_message=None
            )
            db.add(sync_record)

            db.commit()
            logger.info("QB OAuth tokens saved successfully")

        except Exception as e:
            logger.error(f"Failed to save QB tokens: {e}", exc_info=True)
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to save tokens: {e}")

        return {
            "status": "success",
            "message": "QuickBooks authentication successful!",
            "realm_id": realmId,
            "access_token": access_token[:50] + "...",
            "note": f"Save this REALM_ID: {realmId}\nAdd to your .env: QB_REALM_ID={realmId}"
        }

    except requests.HTTPError as e:
        logger.error(f"QB token exchange failed: {e.response.text}")
        raise HTTPException(status_code=400, detail=f"QB token exchange failed: {e.response.text}")
    except Exception as e:
        logger.error(f"QB OAuth callback error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/quickbooks/status")
async def quickbooks_status(db: Session = Depends(get_db)):
    """Check if QuickBooks API is authenticated."""
    from app.models.database import OAuthToken

    try:
        qb_token = db.query(OAuthToken).filter(
            OAuthToken.provider == "quickbooks"
        ).first()

        if qb_token and qb_token.refresh_token:
            return {
                "authenticated": True,
                "last_auth": str(qb_token.updated_at),
                "message": "QuickBooks API is authenticated",
                "realm_id_needed": not bool(settings.qb_realm_id),
            }
        else:
            return {
                "authenticated": False,
                "message": "Please authenticate with QuickBooks",
                "login_url": "/api/auth/quickbooks/login",
            }
    except Exception as e:
        logger.error(f"Error checking QB status: {e}")
        return {
            "authenticated": False,
            "message": "Error checking authentication status",
            "error": str(e),
        }
