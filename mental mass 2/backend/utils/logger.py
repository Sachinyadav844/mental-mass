"""
Logging setup for MentalMass
"""
import logging
import logging.handlers
from config import ERROR_LOG_FILE, ACCESS_LOG_FILE, LOG_FORMAT, LOG_DATE_FORMAT

# ============================================================================
# ERROR LOGGER
# ============================================================================

def setup_error_logger():
    """Setup error logging to file"""
    logger = logging.getLogger('mentalmass_errors')
    logger.setLevel(logging.ERROR)
    
    # File handler
    handler = logging.handlers.RotatingFileHandler(
        ERROR_LOG_FILE,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    handler.setLevel(logging.ERROR)
    formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger


# ============================================================================
# ACCESS LOGGER
# ============================================================================

def setup_access_logger():
    """Setup access logging to file"""
    logger = logging.getLogger('mentalmass_access')
    logger.setLevel(logging.INFO)
    
    # File handler
    handler = logging.handlers.RotatingFileHandler(
        ACCESS_LOG_FILE,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger


# ============================================================================
# GLOBAL LOGGERS
# ============================================================================

error_logger = setup_error_logger()
access_logger = setup_access_logger()


def log_error(error_code, message, details=None):
    """Log error with code and details"""
    error_logger.error(f"[{error_code}] {message} | Details: {details}")


def log_access(endpoint, method, user_id=None, status=200):
    """Log endpoint access"""
    access_logger.info(f"{method} {endpoint} - User: {user_id} - Status: {status}")
