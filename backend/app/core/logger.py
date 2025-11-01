"""
Logging configuration
"""
import logging
import sys
from pythonjsonlogger import jsonlogger

from app.core.config import settings


def setup_logging():
    """Setup application logging"""
    
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(settings.LOG_LEVEL)
    
    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    
    if settings.ENVIRONMENT == "production":
        # Use JSON formatting in production
        formatter = jsonlogger.JsonFormatter(
            "%(timestamp)s %(level)s %(name)s %(message)s",
            timestamp=True
        )
    else:
        # Use standard formatting in development
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    # Setup Sentry if configured
    if settings.SENTRY_DSN:
        import sentry_sdk
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            environment=settings.ENVIRONMENT,
            traces_sample_rate=1.0 if settings.ENVIRONMENT == "development" else 0.1,
        )
    
    return logger

