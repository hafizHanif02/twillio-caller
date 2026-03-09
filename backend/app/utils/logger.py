import logging
import sys
from ..config import settings

# Configure logging
def setup_logger(name: str = "twilio_app") -> logging.Logger:
    """Set up application logger with appropriate formatting."""

    logger = logging.getLogger(name)

    # Set level based on environment
    if settings.is_development:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG if settings.is_development else logging.INFO)

    # Create formatter
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [%(name)s:%(lineno)d] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)

    # Add handler to logger
    if not logger.handlers:
        logger.addHandler(handler)

    return logger


# Global logger instance
logger = setup_logger()
