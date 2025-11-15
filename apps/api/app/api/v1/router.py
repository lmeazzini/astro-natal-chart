"""
API v1 router - aggregates all v1 endpoints.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, charts, geocoding, interpretations, oauth

api_router = APIRouter()

# Authentication endpoints
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["authentication"],
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
