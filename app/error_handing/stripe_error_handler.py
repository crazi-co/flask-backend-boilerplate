"""Stripe specific error handling."""

from typing import Any, Dict, Optional

from app.error_handing.base_error_handler import BaseError



class StripeError(BaseError):
    """Stripe service specific errors."""
    
    def __init__(
        self,
        function_name: str,
        metadata: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None
    ) -> None:
    
        context = {
            "function_name": function_name,
        }

        if metadata:
            context.update(metadata)
        
        super().__init__(
            service = "stripe",
            context = context,
            original_error = original_error
        )
