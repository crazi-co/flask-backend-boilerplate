"""Routes for miscellaneous operations."""

import os
from flask import Response as FlaskResponse

from app.utils.api_responses import APIResponse



class MiscRoute:

    """Misc route functions."""

    @staticmethod
    def health() -> FlaskResponse:
        """Health check."""

        return APIResponse.success("Health check successful.", {"status": "healthy", "service": "crazi-co"}, 200)
    
    @staticmethod
    def version() -> FlaskResponse:
        """Version check."""

        return APIResponse.success("Version check successful.", {"version": os.getenv("VERSION")}, 200)
