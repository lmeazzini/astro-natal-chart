"""
API v1 router - aggregates all v1 endpoints.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    admin,
    admin_blog,
    auth,
    blog,
    cache,
    charts,
    geocoding,
    github,
    growth,
    interpretations,
    oauth,
    password_reset,
    privacy,
    public_charts,
    rag,
    seo,
    timezones,
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

# Timezone endpoints
api_router.include_router(
    timezones.router,
    prefix="/timezones",
    tags=["timezones"],
)

# RAG (Retrieval-Augmented Generation) endpoints
api_router.include_router(
    rag.router,
    tags=["rag"],
)

# Public charts endpoints (no auth required for GET)
api_router.include_router(
    public_charts.router,
    tags=["public-charts"],
)

# Public charts admin endpoints (admin only)
api_router.include_router(
    public_charts.admin_router,
    tags=["admin-public-charts"],
)

# Personal growth suggestions endpoints
api_router.include_router(
    growth.router,
    tags=["personal-growth"],
)

# Blog endpoints (public - no auth required)
api_router.include_router(
    blog.router,
    tags=["blog"],
)

# Blog admin endpoints (admin only)
api_router.include_router(
    admin_blog.router,
    tags=["admin-blog"],
)

# SEO endpoints (sitemap, RSS, robots.txt)
api_router.include_router(
    seo.router,
    tags=["seo"],
)
