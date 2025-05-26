"""
API initialization.
"""

from fastapi import APIRouter, Depends

from app.api.v1.auth import router as auth_router
from app.api.v1.transform import router as transform_router
from app.core.auth import get_current_active_user

# Create main router
router = APIRouter()

# Create v1 router
v1_router = APIRouter(prefix="/v1")

# Include all v1 endpoint routers
v1_router.include_router(transform_router, dependencies=[Depends(get_current_active_user)])
v1_router.include_router(auth_router, prefix="/auth", tags=["authentication"])

# Include versioned router
router.include_router(v1_router)
