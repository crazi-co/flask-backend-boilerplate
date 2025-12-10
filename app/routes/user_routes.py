"""Routes for user operations."""

import os

from flask import request, Response as FlaskResponse
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

import app.data
from app.schemas import User as UserModel
from app.utils.api_responses import APIResponse



class UserRoute:

    """User route functions."""

    @staticmethod
    @app.data.ServiceConfig.authentication.private_authentication
    def view_all(*_args, **_kwargs) -> FlaskResponse:
        """View all users."""

        try:

            limit: int = int(request.args.get("limit", None))
            offset: int = int(request.args.get("offset", None))

            users = [user.model_dump() for user in app.data.ServiceConfig.user.view_all(limit, offset)]

            return APIResponse.success("Users fetched successfully.", users, 200)
 
        except (TypeError, ValueError):
            return APIResponse.schema_error()

    @staticmethod
    @app.data.ServiceConfig.authentication.general_authentication_inactive
    def view(user_id: str, *_args, **kwargs) -> FlaskResponse:
        """View a user."""
        
        if kwargs["role"] == os.getenv("PRIVATE_ROLE"):

            try:
                user = app.data.ServiceConfig.user.view(user_id, UserModel.id)

            except ValueError:
                return APIResponse.resource_presence_error("User")
        
        else:

            user: UserModel = kwargs["user"]

            if user.id != user_id:
                return APIResponse.resource_access_error()

        user = user.model_dump()
        del user["password"]
        del user["stripe_customer_id"]
        del user["google_user_id"]

        return APIResponse.success("User fetched successfully.", user, 200)

    @staticmethod
    @app.data.ServiceConfig.authentication.general_authentication_inactive
    def update(user_id: str, *_args, **kwargs) -> FlaskResponse:
        """Update a user."""

        try:        

            if kwargs["role"] == os.getenv("PRIVATE_ROLE"):

                try:
                    user = app.data.ServiceConfig.user.view(user_id, UserModel.id)

                except ValueError:
                    return APIResponse.resource_presence_error("User")
            
            else:

                user: UserModel = kwargs["user"]

                if user.id != user_id:
                    return APIResponse.resource_access_error()    

            try:
                payload = request.json
                
            except Exception as exc: # pylint: disable = W0718

                if request.is_json:
                    raise ValueError from exc

                else:
                    return APIResponse.empty_body_error()

            if not request.is_json or not payload:
                return APIResponse.empty_body_error()

            forbidden_keys = ["id", "email", "stripe_customer_id", "password", "credits", "is_2fa_enabled", "is_active", "created_at", "updated_at"]

            for key in payload.keys():

                if key in forbidden_keys:
                    raise ValueError

            try:
                user = app.data.ServiceConfig.user.update(user_id, UserModel.id, **payload)

            except ValidationError as exc:
                raise ValueError from exc

            except ValueError:
                return APIResponse.resource_presence_error("User")

            user = user.model_dump()
            del user["password"]
            del user["stripe_customer_id"]
            del user["google_user_id"]

            return APIResponse.success("User updated successfully.", user, 200)
 
        except (KeyError, ValueError, ValidationError, SQLAlchemyError):
            return APIResponse.schema_error()

    @staticmethod
    @app.data.ServiceConfig.authentication.private_authentication
    def update_credits(user_id: str, *_args, **_kwargs) -> FlaskResponse:
        """Update a user's credits."""

        try:         

            try:
                payload = request.json
                
            except Exception as exc: # pylint: disable = W0718

                if request.is_json:
                    raise ValueError from exc

                else:
                    return APIResponse.empty_body_error()

            if not request.is_json or not payload:
                return APIResponse.empty_body_error()

            user_credits: float = round(float(payload["credits"]), 2)

            try:
                app.data.ServiceConfig.user.update_credits(user_id, UserModel.id, user_credits)

            except ValidationError as exc:
                raise ValueError from exc

            except ValueError:
                return APIResponse.resource_presence_error("User")

            user = app.data.ServiceConfig.user.view(user_id, UserModel.id).model_dump()
            del user["password"]
            del user["stripe_customer_id"]
            del user["google_user_id"]

            return APIResponse.success("User's credits updated successfully.", user, 200)
 
        except (KeyError, ValueError, ValidationError, SQLAlchemyError):
            return APIResponse.schema_error()

    @staticmethod
    @app.data.ServiceConfig.authentication.private_authentication
    def delete(user_id: str, *_args, **_kwargs) -> FlaskResponse:
        """Delete a user."""

        try:
            app.data.ServiceConfig.user.delete(user_id, UserModel.id)

        except ValueError:
            return APIResponse.resource_presence_error("User")

        return APIResponse.null()
