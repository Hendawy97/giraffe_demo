"""
Simple FastAPI application without database dependencies for demo.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import structlog

# Import only the demo routes
from app.api.v1.demo import router as demo_router

def create_simple_app() -> FastAPI:
    """
    Create a simple FastAPI app for demo purposes.
    """
    app = FastAPI(
        title="Giraffe Demo API",
        description="Simple demo API for Giraffe SDK integration",
        version="1.0.0-demo",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    
    # Setup logging
    structlog.configure(
        processors=[
            structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(20),  # INFO level
        logger_factory=structlog.WriteLoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include demo routes
    app.include_router(demo_router, prefix="/api/v1/demo", tags=["demo"])
    
    @app.get("/")
    async def root():
        return {"message": "Giraffe Demo API", "status": "running", "mode": "demo"}
    
    @app.get("/health")
    async def health():
        return {"status": "healthy", "mode": "demo"}
    
    return app

# Create the application instance
app = create_simple_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main_simple:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )