from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool, QueuePool
import logging

from app.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

# Create engine with connection pooling
engine = create_engine(
    settings.database_url,
    poolclass=QueuePool,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    pool_pre_ping=True,  # Test connections before using
    pool_recycle=3600,   # Recycle connections after 1 hour
    echo=settings.debug,
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Base class for ORM models
Base = declarative_base()


def get_db() -> Session:
    """Dependency for getting database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Set PostgreSQL specific settings."""
    pass


def init_db():
    """Initialize database (create all tables)."""
    # Import models to register them
    from app.models.database import (  # noqa: F401
        Customer, Product, Invoice, InvoiceLineItem, Payment,
        DailyRevenue, ProductSale, SyncHistory, QueryHistory
    )
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized")


def close_db():
    """Close database connection."""
    engine.dispose()
    logger.info("Database connection closed")
