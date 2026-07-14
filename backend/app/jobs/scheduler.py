import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime

from app.services.zoho_sync import ZohoSyncService
from app.utils.logger import get_logger

logger = get_logger(__name__)

scheduler = BackgroundScheduler()


def sync_zoho_delta():
    """Run incremental (delta) sync from Zoho - runs hourly."""
    logger.info("=== Starting hourly delta sync ===")
    try:
        sync_service = ZohoSyncService()
        results = sync_service.sync_all(full_sync=False)
        logger.info(f"Delta sync completed: {results}")
    except Exception as e:
        logger.error(f"Delta sync failed: {e}", exc_info=True)


def sync_zoho_full():
    """Run full sync from Zoho - runs weekly on Sunday at midnight."""
    logger.info("=== Starting weekly full sync ===")
    try:
        sync_service = ZohoSyncService()
        results = sync_service.sync_all(full_sync=True)
        logger.info(f"Full sync completed: {results}")
    except Exception as e:
        logger.error(f"Full sync failed: {e}", exc_info=True)


def start_scheduler():
    """Start the background scheduler."""
    if scheduler.running:
        logger.warning("Scheduler is already running")
        return

    # Hourly delta sync (every hour at minute 0)
    scheduler.add_job(
        sync_zoho_delta,
        trigger=CronTrigger(minute=0),
        id="zoho_delta_sync",
        name="Zoho Delta Sync (Hourly)",
        replace_existing=True,
    )

    # Weekly full sync (Sunday at 00:00)
    scheduler.add_job(
        sync_zoho_full,
        trigger=CronTrigger(day_of_week=6, hour=0, minute=0),
        id="zoho_full_sync",
        name="Zoho Full Sync (Weekly)",
        replace_existing=True,
    )

    scheduler.start()
    logger.info(f"Scheduler started at {datetime.utcnow()}")
    logger.info("Jobs scheduled:")
    for job in scheduler.get_jobs():
        logger.info(f"  - {job.name} ({job.id}): {job.trigger}")


def stop_scheduler():
    """Stop the background scheduler."""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler stopped")


def trigger_sync_now(full_sync: bool = False):
    """Manually trigger a sync (useful for testing or urgent syncs)."""
    logger.info(f"Manually triggering sync (full={full_sync})")
    try:
        sync_service = ZohoSyncService()
        results = sync_service.sync_all(full_sync=full_sync)
        logger.info(f"Manual sync completed: {results}")
        return results
    except Exception as e:
        logger.error(f"Manual sync failed: {e}", exc_info=True)
        raise
