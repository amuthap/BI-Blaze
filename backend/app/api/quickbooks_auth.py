"""QuickBooks OAuth authentication endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.quickbooks_oauth_v2 import QuickBooksOAuthV2
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
        oauth = QuickBooksOAuthV2()
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
    realmId: str = Query(...),
    state: str = Query(None)
):
    """Handle OAuth callback from QuickBooks."""
    db = None
    try:
        logger.info(f"Received OAuth callback with code: {code[:20]}... and realmId: {realmId}")

        # Try to get database connection, but don't fail if unavailable
        try:
            from app.db.database import SessionLocal
            db = SessionLocal()
        except Exception as e:
            logger.warning(f"Could not establish database connection: {e}")

        oauth = QuickBooksOAuthV2()
        logger.info(f"Created OAuth client")

        # Exchange code for token using official SDK
        logger.info(f"Exchanging code for token...")
        token_data = oauth.exchange_code_for_token(code, realmId)
        logger.info(f"Token exchange successful: {list(token_data.keys())}")

        # Save token to database if available
        if db:
            logger.info(f"Saving token to database...")
            oauth.save_token(db, token_data)
            logger.info(f"Token saved successfully")
        else:
            logger.warning("Database not available - token not saved")

        # Update realm ID in settings/database
        settings.qb_realm_id = realmId
        logger.info(f"Authorized QuickBooks. Realm ID: {realmId}")

        # Skip initial sync - will be done manually or on schedule
        sync_status = "skipped"
        logger.info("Skipping initial sync (will run on schedule)")

        logger.info(f"Callback successful (sync={sync_status}), redirecting to settings...")
        # Redirect to settings page after successful authorization
        frontend_url = "https://blazebi.hyperbig.com" if settings.app_env == "production" else "http://localhost:3000"
        redirect_url = f"{frontend_url}/settings?qb=success"
        logger.info(f"Redirect URL: {redirect_url}, Environment: {settings.app_env}")
        return RedirectResponse(url=redirect_url, status_code=302)

    except Exception as e:
        logger.error(f"OAuth callback error: {str(e)}", exc_info=True)
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        # Redirect to settings with error
        frontend_url = "https://blazebi.hyperbig.com" if settings.app_env == "production" else "http://localhost:3000"
        redirect_url = f"{frontend_url}/settings?qb=error"
        logger.error(f"Error redirect URL: {redirect_url}, Environment: {settings.app_env}")
        return RedirectResponse(url=redirect_url, status_code=302)

    finally:
        if db:
            try:
                db.close()
            except:
                pass


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
    """Check QuickBooks connection status with sync details."""
    try:
        from app.models.database import OAuthToken, SyncHistory
        from datetime import datetime

        token = db.query(OAuthToken).filter(OAuthToken.provider == "quickbooks").first()

        if not token:
            return {
                "connected": False,
                "message": "QuickBooks not connected"
            }

        # Check last sync attempt (QB-specific)
        last_sync = db.query(SyncHistory).filter(
            SyncHistory.entity_type.in_(["qb_customer", "qb_product", "qb_invoice", "qb_payment"])
        ).order_by(SyncHistory.completed_at.desc()).first()

        if not last_sync:
            return {
                "connected": True,
                "realm_id": settings.qb_realm_id,
                "expires_at": token.expires_at,
                "message": "QB token valid - Ready to sync (no previous sync history)",
                "last_sync_status": None
            }

        if last_sync.status.value == "failed":
            return {
                "connected": True,
                "realm_id": settings.qb_realm_id,
                "expires_at": token.expires_at,
                "message": f"QB token valid - Last sync FAILED ({last_sync.error_message})",
                "last_sync_status": "failed",
                "last_sync_error": last_sync.error_message,
                "last_sync_at": last_sync.completed_at
            }

        return {
            "connected": True,
            "realm_id": settings.qb_realm_id,
            "expires_at": token.expires_at,
            "message": f"QB connected - Last synced: {last_sync.completed_at}",
            "last_sync_status": last_sync.status.value,
            "last_sync_at": last_sync.completed_at
        }

    except Exception as e:
        logger.error(f"Error checking QB status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync")
async def sync_quickbooks(db: Session = Depends(get_db)):
    """Manually trigger QuickBooks sync."""
    from app.models.database import SyncHistory, SyncStatusEnum
    from datetime import datetime

    sync_record = SyncHistory(
        entity_type="qb_customer",  # Representative entity
        sync_type="full",
        status=SyncStatusEnum.in_progress,
        started_at=datetime.utcnow()
    )
    db.add(sync_record)
    db.commit()

    try:
        sync = QuickBooksSync(db)
        await sync.sync_all()

        sync_record.status = SyncStatusEnum.completed
        sync_record.completed_at = datetime.utcnow()
        db.commit()

        return {
            "message": "QuickBooks sync completed successfully",
            "status": "completed"
        }

    except Exception as e:
        logger.error(f"QuickBooks sync error: {str(e)}")
        sync_record.status = SyncStatusEnum.failed
        sync_record.error_message = str(e)
        sync_record.completed_at = datetime.utcnow()
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))
