"""QuickBooks OAuth authentication endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.quickbooks_oauth import QuickBooksOAuth
from app.services.quickbooks_sync import QuickBooksSync
from app.config import get_settings
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth/quickbooks", tags=["quickbooks-auth"])

settings = get_settings()


@router.get("/authorize")
async def authorize_quickbooks(db: Session = Depends(get_db)):
    """Get QuickBooks authorization URL."""
    try:
        oauth = QuickBooksOAuth()
        auth_url = oauth.get_authorization_url()

        return {
            "authorization_url": auth_url,
            "message": "Click the URL to authorize QuickBooks access"
        }
    except Exception as e:
        logger.error(f"Error generating auth URL: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/callback")
async def oauth_callback(
    code: str = Query(...),
    realm_id: str = Query(...),
    state: str = Query(None),
    db: Session = Depends(get_db)
):
    """Handle OAuth callback from QuickBooks."""
    try:
        logger.info(f"Received OAuth callback with code and realm_id: {realm_id}")

        oauth = QuickBooksOAuth()

        # Exchange code for token
        token_data = await oauth.exchange_code_for_token(code)

        # Save token to database
        oauth.save_token(db, token_data)

        # Update realm ID in settings/database
        settings.qb_realm_id = realm_id
        logger.info(f"Authorized QuickBooks. Realm ID: {realm_id}")

        # Start sync
        try:
            sync = QuickBooksSync(db)
            await sync.sync_all()
            logger.info("Initial QuickBooks sync completed")
        except Exception as e:
            logger.error(f"Error during initial sync: {str(e)}")
            # Don't fail if sync fails - token is saved

        return {
            "message": "QuickBooks authorized successfully!",
            "realm_id": realm_id,
            "sync_started": True
        }

    except Exception as e:
        logger.error(f"OAuth callback error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/disconnect")
async def disconnect_quickbooks(db: Session = Depends(get_db)):
    """Disconnect QuickBooks account."""
    try:
        from app.models.database import OAuthToken

        token = db.query(OAuthToken).filter(OAuthToken.provider == "quickbooks").first()
        if token:
            db.delete(token)
            db.commit()
            logger.info("QuickBooks account disconnected")

        return {"message": "QuickBooks disconnected successfully"}

    except Exception as e:
        logger.error(f"Error disconnecting QuickBooks: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def quickbooks_status(db: Session = Depends(get_db)):
    """Check QuickBooks connection status."""
    try:
        from app.models.database import OAuthToken

        token = db.query(OAuthToken).filter(OAuthToken.provider == "quickbooks").first()

        if not token:
            return {
                "connected": False,
                "message": "QuickBooks not connected"
            }

        return {
            "connected": True,
            "realm_id": settings.qb_realm_id,
            "expires_at": token.expires_at,
            "message": "QuickBooks connected"
        }

    except Exception as e:
        logger.error(f"Error checking QB status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync")
async def sync_quickbooks(db: Session = Depends(get_db)):
    """Manually trigger QuickBooks sync."""
    try:
        sync = QuickBooksSync(db)
        await sync.sync_all()

        return {
            "message": "QuickBooks sync completed successfully",
            "status": "completed"
        }

    except Exception as e:
        logger.error(f"QuickBooks sync error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
