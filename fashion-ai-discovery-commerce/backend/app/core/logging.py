import logging
import sys
from pathlib import Path
from typing import Dict, Any

import structlog
from app.core.config import settings


def setup_logging() -> None:
    """Setup structured logging"""
    
    # Create logs directory if it doesn't exist
    log_file_path = Path(settings.LOG_FILE)
    log_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.LOG_LEVEL.upper()),
    )
    
    # File handler
    file_handler = logging.FileHandler(settings.LOG_FILE)
    file_handler.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    
    # Get root logger and add handlers
    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance"""
    return structlog.get_logger(name)


class LoggingMixin:
    """Mixin class to add logging capability to any class"""
    
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
    
    def log_event(self, event: str, **kwargs: Any) -> None:
        """Log an event with additional context"""
        self.logger.info(event, **kwargs)
    
    def log_error(self, error: str, **kwargs: Any) -> None:
        """Log an error with additional context"""
        self.logger.error(error, **kwargs)
    
    def log_debug(self, message: str, **kwargs: Any) -> None:
        """Log a debug message with additional context"""
        self.logger.debug(message, **kwargs)