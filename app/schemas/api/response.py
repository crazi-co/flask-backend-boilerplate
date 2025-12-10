"""Response API schema."""

from typing import Dict, Any, Optional, List, Union

from pydantic import BaseModel



class Response(BaseModel):
    """Response model."""

    status: str
    message: str
    data: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]]
