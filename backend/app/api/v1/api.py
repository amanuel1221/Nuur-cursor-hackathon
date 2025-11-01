"""
API v1 router
"""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, anti_theft, paths, emergency, users

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(anti_theft.router, prefix="/anti-theft", tags=["anti-theft"])
api_router.include_router(paths.router, prefix="/paths", tags=["path-tracking"])
api_router.include_router(emergency.router, prefix="/emergency", tags=["emergency"])

