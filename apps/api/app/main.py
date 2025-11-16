"""
Main FastAPI application entry point.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import close_db, init_db
from app.core.logging_config import configure_logging, intercept_uvicorn_logs
from app.core.middleware import RequestLoggingMiddleware
from app.core.rate_limit import limiter
from app.middleware.security import SecurityHeadersMiddleware

# Configure logging early (before app creation)
configure_logging()
intercept_uvicorn_logs()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API para geração e análise de mapas natais com astrologia tradicional",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Add rate limiter to app state
app.state.limiter = limiter

# Add rate limit exceeded exception handler
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]

# Request logging middleware (should be first to capture all requests)
app.add_middleware(RequestLoggingMiddleware)

# Security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event() -> None:
    """Initialize application on startup."""
    logger.info(
        "Starting application",
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
        debug=settings.DEBUG,
    )

    # Initialize database (in production, use Alembic migrations instead)
    if settings.DEBUG:
        await init_db()
        logger.debug("Database initialized")


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Cleanup on shutdown."""
    logger.info("Shutting down application")
    await close_db()
    logger.info("Database connections closed")


@app.get("/", tags=["Health"])
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {
        "message": "Real Astrology API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health_check() -> JSONResponse:
    """Health check endpoint for monitoring."""
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "environment": settings.ENVIRONMENT,
        },
    )


# Include API routers
app.include_router(api_router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
