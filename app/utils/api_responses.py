"""API responses utility."""

from typing import Optional, Union, Dict, Any, List
from flask import jsonify, Response as FlaskResponse

from app.schemas import Response as ResponseModel



class APIResponse:
    """API responses utility functions."""

    def __init__(self) -> None:
        pass

    @staticmethod
    def success(message: str, data: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None, status_code: int = 200) -> FlaskResponse:
        """Success response."""
        
        response = ResponseModel(
            status = "success",
            message = message,
            data = data
        )

        return jsonify(response.model_dump()), status_code

    @staticmethod
    def empty_body_error() -> FlaskResponse:
        """Empty body error."""

        response = ResponseModel(
            status = "error",
            message = "Request body is empty.",
            data = None
        )

        return jsonify(response.model_dump()), 400
    
    @staticmethod
    def schema_error() -> FlaskResponse:
        """Schema error."""

        response = ResponseModel(
            status = "error",
            message = "One or more required parameters are either not given or have invalid schema.",
            data = None
        )

        return jsonify(response.model_dump()), 400

    @staticmethod
    def authentication_error(is_2fa_enabled: bool = False) -> FlaskResponse:
        """Authentication error."""

        response = ResponseModel(
            status = "error",
            message = "Authorization header or OTP is either missing, invalid or expired.",
            data = None
        )

        if is_2fa_enabled:
            response.data = {"is_2fa_enabled": True}

        return jsonify(response.model_dump()), 401

    @staticmethod
    def resource_presence_error(resource: str, found: bool = False) -> FlaskResponse:
        """Resource presence error."""

        if not found:

            message = f"{resource} with the given identifier does not exist."
            status_code = 404

        else:

            message = f"{resource} with the given identifier already exists."
            status_code = 400

        response = ResponseModel(
            status = "error",
            message = message,
            data = None
        )

        return jsonify(response.model_dump()), status_code

    @staticmethod
    def resource_access_error() -> FlaskResponse:
        """Resource access error."""

        response = ResponseModel(
            status = "error",
            message = "You do not have access to the requested resource.",
            data = None
        )

        return jsonify(response.model_dump()), 403
    
    @staticmethod
    def user_inactive_error() -> FlaskResponse:
        """User inactive error."""

        response = ResponseModel(
            status = "error",
            message = "Please activate your account to access the requested resource.",
            data = None
        )

        return jsonify(response.model_dump()), 401
    
    @staticmethod
    def credits_error() -> FlaskResponse:
        """Credits error."""

        response = ResponseModel(
            status = "error",
            message = "You do not have enough credits to perform this action.",
            data = None
        )

        return jsonify(response.model_dump()), 403

    @staticmethod
    def credits_rate_not_found_error() -> FlaskResponse:
        """Credits rate not found error."""

        response = ResponseModel(
            status = "error",
            message = "No credits rate found for the given amount.",
            data = None
        )

        return jsonify(response.model_dump()), 404

    @staticmethod
    def route_not_found_error() -> FlaskResponse:
        """Route not found error."""

        response = ResponseModel(
            status = "error",
            message = "The requested route does not exist.",
            data = None
        )

        return jsonify(response.model_dump()), 404
    
    @staticmethod
    def method_not_allowed_error() -> FlaskResponse:
        """Method not allowed error."""

        response = ResponseModel(
            status = "error",
            message = "The requested method is not allowed for this route.",
            data = None
        )

        return jsonify(response.model_dump()), 405

    @staticmethod
    def rate_limit_error() -> FlaskResponse:
        """Rate limit error."""

        response = ResponseModel(
            status = "error",
            message = "You have exceeded the rate limit.",
            data = None
        )

        return jsonify(response.model_dump()), 429
    
    @staticmethod
    def unidentified_error() -> FlaskResponse:
        """Unidentified error."""

        response = ResponseModel(
            status = "error",
            message = "Something went wrong.",
            data = None
        )

        return jsonify(response.model_dump()), 500

    @staticmethod
    def null() -> FlaskResponse:
        """Null response."""

        return "", 204
        