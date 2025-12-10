"""AWS SES specific error handling."""

from typing import Any, Dict, Optional

from app.error_handing.base_error_handler import BaseError



class AWSError(BaseError):
    """AWS SES service specific errors."""
    
    def __init__(
        self, 
        message: str, 
        *,
        service_name: Optional[str] = None,
        operation: Optional[str] = None,
        recipient: Optional[str] = None,
        error_code: Optional[str] = None,
        error_type: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None
    ) -> None:
    
        context = {
            "message": message,
        }

        if service_name:
            context["service_name"] = service_name

        if operation:
            context["operation"] = operation

        if recipient:
            context["recipient"] = recipient

        if error_code:
            context["error_code"] = error_code

        if error_type:
            context["error_type"] = error_type

        if metadata:
            context.update(metadata)
        
        super().__init__(
            service = "aws",
            context = context,
            original_error = original_error
        )
