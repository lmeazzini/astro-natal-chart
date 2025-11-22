"""
API v1 router - aggregates all v1 endpoints.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    admin,
    auth,
    cache,
    charts,
    geocoding,
    github,
    interpretations,
    oauth,
    password_reset,
    privacy,
    users,
)

api_router = APIRouter()

# Authentication endpoints
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["authentication"],
)

# User profile endpoints
api_router.include_router(
    users.router,
    prefix="/users",
    tags=["users"],
)

# Birth chart endpoints
api_router.include_router(
    charts.router,
    prefix="/charts",
    tags=["birth-charts"],
)

# OAuth endpoints
api_router.include_router(
    oauth.router,
    prefix="/oauth",
    tags=["oauth"],
)

# Geocoding endpoints
api_router.include_router(
    geocoding.router,
    prefix="/geocoding",
    tags=["geocoding"],
)

# Interpretation endpoints
api_router.include_router(
    interpretations.router,
    tags=["interpretations"],
)

# Password reset endpoints
api_router.include_router(
    password_reset.router,
    tags=["password-reset"],
)

# Privacy & LGPD endpoints
api_router.include_router(
    privacy.router,
    tags=["privacy"],
)

# Admin endpoints (restricted)
api_router.include_router(
    admin.router,
    tags=["admin"],
)

# Cache management endpoints
api_router.include_router(
    cache.router,
    prefix="/cache",
    tags=["cache"],
)

# GitHub API endpoints
api_router.include_router(
    github.router,
    prefix="/github",
    tags=["github"],
)
