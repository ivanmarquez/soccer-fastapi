import logging
from ..config import settings

# Ensure LOG_LEVEL is a valid logging level
valid_levels = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL
}

log_level = valid_levels.get(settings.LOG_LEVEL.upper(), logging.INFO)

# Configure the logging settings
logging.basicConfig(level=log_level, format=settings.LOG_FORMAT)
logger = logging.getLogger(__name__)

def log_message(message: str, level: str = "info"):
    try:
        level = level.upper()
        if level == "INFO":
            logger.info(message)
        elif level == "WARNING":
            logger.warning(message)
        elif level == "ERROR":
            logger.error(message)
        elif level == "CRITICAL":
            logger.critical(message)
        else:
            logger.debug(message)
    except Exception as e:
        logger.error(f"Logging error: {e}")
    return message
