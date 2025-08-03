"""
API v1 routes.
"""

from fastapi import APIRouter

from app.api.v1 import demo
from app.core.config import get_settings

try:
    from app.api.v1 import auth, projects, users, websocket
    HAS_DB_MODULES = True
except ImportError:
    HAS_DB_MODULES = False


router = APIRouter()

# Always include demo routes
router.include_router(demo.router, prefix="/demo", tags=["demo"])

# Include database-dependent routes only if available and not in demo mode
settings = get_settings()
if HAS_DB_MODULES and not settings.DEMO_MODE:
    try:
        router.include_router(auth.router, prefix="/auth", tags=["authentication"])
        router.include_router(users.router, prefix="/users", tags=["users"])
        router.include_router(projects.router, prefix="/projects", tags=["projects"])
        router.include_router(websocket.router, prefix="/ws", tags=["websocket"])
    except Exception:
        # Fallback to demo mode if database modules fail
        pass