"""
Loguru logging configuration for the application.

Provides structured logging with:
- Colorized console output in development
- JSON structured logs in production
- Automatic log rotation
- Context binding for request_id and user_id
"""

import sys
from pathlib import Path

from loguru import logger

from app.core.config import settings


def configure_logging() -> None:
    """
    Configure loguru logger based on environment.

    Development: Colorized console logs with DEBUG level
    Production: JSON structured logs with INFO level + file rotation
    """
    # Remove default handler
    logger.remove()

    # Determine log level
    log_level = "DEBUG" if settings.DEBUG else "INFO"

    if settings.DEBUG:
        # Development: colorized console output
        logger.add(
            sys.stderr,
            format=(
                "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                "<level>{message}</level> | "
                "{extra}"
            ),
            level=log_level,
            colorize=True,
            backtrace=True,
            diagnose=True,
        )
    else:
        # Production: JSON structured logs to stderr
        logger.add(
            sys.stderr,
            format="{message}",
            level=log_level,
            serialize=True,  # JSON output
            backtrace=False,
            diagnose=False,
        )

        # Production: file logs with rotation
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        logger.add(
            log_dir / "astro_{time:YYYY-MM-DD}.log",
            rotation="500 MB",  # Rotate when file reaches 500MB
            retention="30 days",  # Keep logs for 30 days
            compression="zip",  # Compress rotated logs
            level=log_level,
            serialize=True,  # JSON output
            backtrace=True,
            diagnose=False,
        )

    logger.info(
        "Logging configured",
        environment="development" if settings.DEBUG else "production",
        level=log_level,
    )


def intercept_uvicorn_logs() -> None:
    """
    Intercept uvicorn's standard logging and redirect to loguru.

    This ensures all application logs go through loguru for consistency.
    """
    import logging

    class InterceptHandler(logging.Handler):
        """Intercept standard logging and redirect to loguru."""

        def emit(self, record: logging.LogRecord) -> None:
            """Emit a log record to loguru."""
            # Get corresponding Loguru level if it exists
            try:
                level: str | int = logger.level(record.levelname).name
            except ValueError:
                level = record.levelno

            # Find caller from where the logged message originated
            frame = logging.currentframe()
            depth = 2
            while frame:
                if frame.f_code.co_filename != logging.__file__:
                    break
                next_frame = frame.f_back
                if next_frame is None:
                    break
                frame = next_frame
                depth += 1

            logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

    # Intercept standard logging
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    # Apply to all existing loggers
    for name in logging.root.manager.loggerDict.keys():
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True
