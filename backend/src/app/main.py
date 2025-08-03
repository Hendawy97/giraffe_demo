"""
FastAPI application factory and main entry point.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.api.v1 import router as api_v1_router
from app.core.config import get_settings
from app.core.logging import setup_logging

# Try to import database modules, fallback if not available
try:
    from app.db.session import engine, Base
    HAS_DATABASE = True
except ImportError:
    HAS_DATABASE = False
    engine = None
    Base = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan context manager.
    Handles startup and shutdown events.
    """
    logger = structlog.get_logger()
    
    # Startup
    logger.info("Starting up Giraffe Demo Backend...")
    
    settings = get_settings()
    
    # Skip database setup in demo mode if DB not available
    try:
        if HAS_DATABASE and not settings.DEMO_MODE:
            # Create database tables
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created/verified")
        else:
            logger.info("Running in DEMO MODE - skipping database setup")
            settings.DEMO_MODE = True
    except Exception as e:
        logger.warning("Database connection failed, running in demo mode", error=str(e))
        settings.DEMO_MODE = True
    
    logger.info("Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    if HAS_DATABASE and not settings.DEMO_MODE and engine:
        try:
            await engine.dispose()
        except Exception:
            pass
    logger.info("Application shutdown complete")


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        FastAPI: Configured FastAPI application instance
    """
    settings = get_settings()
    
    # Setup logging
    setup_logging(settings.LOG_LEVEL)
    
    # Create FastAPI instance
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="Scalable FastAPI backend for Giraffe SDK demo application",
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
    )
    
    # Add security middleware
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS,
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include API routers
    app.include_router(
        api_v1_router,
        prefix=settings.API_V1_STR,
    )
    
    @app.get("/health")
    async def health_check() -> dict[str, str]:
        """Health check endpoint."""
        return {"status": "healthy", "version": "0.1.0"}
    
    return app


# Create the application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    settings = get_settings()
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )