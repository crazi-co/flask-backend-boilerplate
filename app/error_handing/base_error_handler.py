"""Base error handler with logging integration."""

from typing import Any, Dict, Optional

from app.utils import get_logger



class BaseError(Exception):
    """Base exception class for all service errors."""
    
    def __init__(
        self,
        service: str,
        context: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None
    ) -> None:
    
        self.service = service
        self.context = context or {}
        self.original_error = original_error
        
        if context:

            details = ", ".join(f"{key} = {value}" for key, value in context.items())
            error_string = f"[{service}] ({details})"

        else:
            error_string = f"[{service}]"
        
        self._log_error(error_string)

    def _log_error(self, error_string: str) -> None:
        """Log the error with human-readable message."""
        
        logger = get_logger(self.service)
        
        logger.error(
            error_string,
            exc_info = self.original_error
        )
