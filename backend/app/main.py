import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.db.database import init_db, close_db, get_db
from app.utils.logger import setup_logging, get_logger
from app.jobs.scheduler import start_scheduler, stop_scheduler

# Setup logging
setup_logging()
logger = get_logger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage app startup and shutdown."""
    # Startup
    logger.info(f"Starting {settings.app_name} in {settings.app_env} mode")
    init_db()
    start_scheduler()
    logger.info("App startup complete")

    yield

    # Shutdown
    logger.info("Shutting down app")
    stop_scheduler()
    close_db()
    logger.info("App shutdown complete")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title=settings.app_name,
        description="AI-powered Business Intelligence System",
        version="0.1.0",
        lifespan=lifespan,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:3001",
            "http://127.0.0.1:3001",
            "*",  # Allow all for development
        ] if settings.debug else ["https://yourdomain.com"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Health check endpoints (both paths for compatibility)
    @app.get("/health")
    @app.get("/api/health")
    async def health():
        return {
            "status": "ok",
            "app": settings.app_name,
            "env": settings.app_env,
            "version": "0.1.0",
        }

    # Welcome endpoint
    @app.get("/")
    async def root():
        return {
            "message": f"Welcome to {settings.app_name}",
            "docs_url": "/docs",
            "health_url": "/health",
            "api_endpoints": {
                "dashboard": "/api/dashboard/*",
                "chat": "/api/query/chat",
                "insights": "/api/query/insights",
            }
        }

    # Include API routers
    from app.api.auth import router as auth_router
    from app.api.dashboard import router as dashboard_router
    from app.api.query import router as query_router
    from app.api.details import router as details_router
    from app.api.reports import router as reports_router

    app.include_router(auth_router)
    app.include_router(dashboard_router)
    app.include_router(query_router)
    app.include_router(details_router)
    app.include_router(reports_router)

    # Mock data endpoint (for development)
    @app.post("/dev/populate-mock-data")
    async def populate_mock_data(db = Depends(get_db)):
        """Populate database with mock data for development."""
        if not settings.debug:
            raise HTTPException(status_code=403, detail="Only available in debug mode")

        from app.services.mock_data import populate_mock_data as generate_mock
        result = generate_mock(db)

        return {
            "status": "success",
            "customers": len(result["customers"]),
            "products": len(result["products"]),
            "invoices": len(result["invoices"]),
            "payments": len(result["payments"]),
            "message": "Mock data populated successfully",
        }

    logger.info("FastAPI app created and configured")
    logger.info("API endpoints registered: /api/dashboard/*, /api/query/*")
    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )
