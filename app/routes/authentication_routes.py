"""Routes for authentication operations."""

import os
import secrets
import string
import time
from typing import List

import bcrypt
from flask import request, Response as FlaskResponse
from google.oauth2 import id_token
from google.auth.transport import requests
from google.auth.exceptions import GoogleAuthError
from jwt.exceptions import DecodeError
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

import app.data
from app.schemas import Session as SessionModel
from app.schemas import User as UserModel
from app.schemas.database.otp import OTPType
from app.utils.api_responses import APIResponse



class AuthenticationRoute:

    """Authentication route functions."""
    
    @staticmethod
    @app.data.ServiceConfig.authentication.static_authentication
    def register(*_args, **kwargs) -> FlaskResponse:
        """Register a new user."""

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
    
            first_name: str = payload["first_name"]
            last_name: str = payload["last_name"]
            email: str = payload["email"]
            password: str = payload["password"]

            if len(password) < 8:
                raise ValueError

            try:
                user = app.data.ServiceConfig.user.create(first_name, last_name, email, password)

            except ValueError:
                return APIResponse.resource_presence_error("User", True)

            otp = app.data.ServiceConfig.otp.create(user.id, OTPType.ACTIVATION)
            
            session = app.data.ServiceConfig.session.create(user.id)
            
            app.data.ServiceConfig.email.welcome(user.email, otp.code, user.id, session.token)
            
            user = user.model_dump()
            user["token"] = session.token

            if kwargs["role"] != os.getenv("PRIVATE_ROLE"):

                del user["password"]
                del user["stripe_customer_id"]
                del user["google_user_id"]

            return APIResponse.success("User registered successfully.", user, 201)
 
        except (KeyError, ValueError, ValidationError, SQLAlchemyError):
            return APIResponse.schema_error()

    @staticmethod
    def google_oauth() -> FlaskResponse:
        """Register a new user via Google OAuth."""

        try:

            if not (request.json):
                return APIResponse.empty_body_error()
    
            token: str = request.json["id_token"]

            try:

                google_user = id_token.verify_oauth2_token(
                    token,
                    requests.Request(),
                    os.getenv("GOOGLE_CLIENT_ID")
                )

                email = google_user["email"]
                first_name = google_user.get("name", None)
                google_user_id = google_user["sub"]

            except (GoogleAuthError, ValueError):
                return APIResponse.authentication_error()

            try:

                user = app.data.ServiceConfig.user.view(email, UserModel.email)

                if user.google_user_id is None:

                    data = {
                        "google_user_id": google_user_id,
                        "is_active": True,
                    }

                    user = app.data.ServiceConfig.user.update(user.id, UserModel.id, **data)

                message = "User logged in successfully."

            except ValueError:

                password = "".join(secrets.choice(string.ascii_letters + string.digits + string.punctuation) for _ in range(16))

                user = app.data.ServiceConfig.user.create(first_name, None, email, password, google_user_id = google_user_id, is_active = True)

                app.data.ServiceConfig.email.password(email, password)

                message = "User registered successfully."

            session = app.data.ServiceConfig.session.create(user.id)
            
            user = user.model_dump()
            user["token"] = session.token

            del user["password"]
            del user["stripe_customer_id"]
            del user["google_user_id"]

            return APIResponse.success(message, user, 201)
 
        except (KeyError, ValueError, ValidationError):
            return APIResponse.schema_error()

    @staticmethod
    @app.data.ServiceConfig.authentication.basic_authentication
    def login(*_args, **kwargs) -> FlaskResponse:
        """Login a user."""

        try:

            user: UserModel = kwargs["user"]

            if user.is_2fa_enabled:

                try:
                    payload = request.json
                    
                except Exception as exc: # pylint: disable = W0718

                    if request.is_json:
                        raise ValueError from exc

                    else:
                        
                        app.data.ServiceConfig.session.delete(kwargs["token"], SessionModel.token)
                        return APIResponse.authentication_error(is_2fa_enabled = True)

                if not request.is_json or not payload:
                    
                    app.data.ServiceConfig.session.delete(kwargs["token"], SessionModel.token)
                    return APIResponse.authentication_error(is_2fa_enabled = True)

                code: str = payload["code"]

                try:
                    otp = app.data.ServiceConfig.otp.view(user.id, OTPType.TWO_FACTOR_AUTH)

                except ValueError:

                    app.data.ServiceConfig.session.delete(kwargs["token"], SessionModel.token)
                    return APIResponse.authentication_error(is_2fa_enabled = True)

                if otp.code != code:

                    app.data.ServiceConfig.session.delete(kwargs["token"], SessionModel.token)
                    return APIResponse.authentication_error(is_2fa_enabled = True)

                if time.time() > otp.expires_at.timestamp():

                    app.data.ServiceConfig.session.delete(kwargs["token"], SessionModel.token)
                    return APIResponse.authentication_error(is_2fa_enabled = True)

                app.data.ServiceConfig.otp.delete(user.id, OTPType.TWO_FACTOR_AUTH)
            
            user = user.model_dump()
            del user["password"]
            del user["stripe_customer_id"]
            del user["google_user_id"]
            
            user["token"] = kwargs["token"]

            return APIResponse.success("User logged in successfully.", user)

        except (KeyError, ValueError, ValidationError, SQLAlchemyError):

            app.data.ServiceConfig.session.delete(kwargs["token"], SessionModel.token)
            return APIResponse.schema_error()

    @staticmethod
    @app.data.ServiceConfig.authentication.general_authentication_inactive
    def logout(*_args, **kwargs) -> FlaskResponse:
        """Logout a user."""

        if kwargs["role"] != os.getenv("USER_ROLE"):
            return APIResponse.resource_access_error()

        app.data.ServiceConfig.session.delete(kwargs["token"], SessionModel.token)

        return APIResponse.null()

    @staticmethod
    def change_password(user_email: str, *_args, **_kwargs) -> FlaskResponse:
        """Change a user's password."""

        try:            

            try:

                token: str = None

                authorization: str = request.headers[os.getenv("AUTHORIZATION_HEADER")]

                if authorization == os.getenv("PRIVATE_API_KEY"):

                    try:
                        user = app.data.ServiceConfig.user.view(user_email, UserModel.email)

                    except ValueError:
                        return APIResponse.resource_presence_error("User")

                elif authorization == os.getenv("PUBLIC_API_KEY"):

                    try:
                        user = app.data.ServiceConfig.user.view(user_email, UserModel.email)

                    except ValueError:
                        return APIResponse.resource_presence_error("User")

                else:

                    authorization: List[str] = authorization.split(" ")

                    if authorization[0] != "Bearer":
                        raise ValueError

                    elif authorization[1].startswith("crazi_couser_"):

                        token = authorization[1].replace("crazi_couser_", "")
                        
                    else:
                        raise ValueError

                    user = app.data.ServiceConfig.authentication.validate_jwt(token)

                    token = "crazi_couser_" + token

                    if user.email != user_email:
                        return APIResponse.resource_access_error()
                    
            except (KeyError, ValueError, DecodeError):
                return APIResponse.authentication_error()

            try:
                payload = request.json
                
            except Exception as exc: # pylint: disable = W0718

                if request.is_json:
                    raise ValueError from exc

                else:
                    return APIResponse.empty_body_error()

            if not request.is_json or not payload:
                return APIResponse.empty_body_error()
    
            password: str = payload["password"]
            code: str = payload["code"]

            otp = app.data.ServiceConfig.otp.view(user.id, OTPType.CHANGE_PASSWORD)

            if otp.code != code:
                return APIResponse.authentication_error()

            if time.time() > otp.expires_at.timestamp():
                return APIResponse.authentication_error()

            app.data.ServiceConfig.user.update(user.id, UserModel.id, password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8"))

            app.data.ServiceConfig.otp.delete(user.id, OTPType.CHANGE_PASSWORD)

            user_sessions = app.data.ServiceConfig.session.view_all(user.id)

            for session in user_sessions:

                if token and session.token == token:
                    continue

                app.data.ServiceConfig.session.delete(session.id, SessionModel.id)

            return APIResponse.success("User password changed successfully.", None, 200)
 
        except (KeyError, ValueError, ValidationError, SQLAlchemyError):
            return APIResponse.schema_error()

    @staticmethod
    @app.data.ServiceConfig.authentication.static_authentication
    def send_otp(user_email: str, otp_type: str, *_args, **_kwargs) -> FlaskResponse:
        """Send an OTP to a user."""

        try:

            try:
                user = app.data.ServiceConfig.user.view(user_email, UserModel.email)

            except ValueError:
                return APIResponse.resource_presence_error("User")

            otp = app.data.ServiceConfig.otp.create(user.id, otp_type)

            app.data.ServiceConfig.email.otp(user.email, otp.code)

            return APIResponse.success("OTP sent successfully.", None, 201)
 
        except (KeyError, ValueError, ValidationError, SQLAlchemyError):
            return APIResponse.schema_error()

    @staticmethod
    @app.data.ServiceConfig.authentication.static_authentication
    def activate(user_email: str, *_args, **_kwargs) -> FlaskResponse:
        """Activate a user."""

        try:        

            try:
                user = app.data.ServiceConfig.user.view(user_email, UserModel.email)

            except ValueError:
                return APIResponse.resource_presence_error("User")

            try:
                payload = request.json
                
            except Exception as exc: # pylint: disable = W0718

                if request.is_json:
                    raise ValueError from exc

                else:
                    return APIResponse.empty_body_error()

            if not request.is_json or not payload:
                return APIResponse.empty_body_error()
    
            code: str = payload["code"]

            try:
                otp = app.data.ServiceConfig.otp.view(user.id, OTPType.ACTIVATION)

            except ValueError:
                return APIResponse.authentication_error()

            if otp.code != code:
                return APIResponse.authentication_error()

            if time.time() > otp.expires_at.timestamp():
                return APIResponse.authentication_error()

            user = app.data.ServiceConfig.user.update(user.id, UserModel.id, is_active = True)

            app.data.ServiceConfig.otp.delete(user.id, OTPType.ACTIVATION)

            user = user.model_dump()
            del user["password"]
            del user["stripe_customer_id"]
            del user["google_user_id"]

            return APIResponse.success("User activated successfully.", user, 200)
 
        except (KeyError, ValueError, ValidationError, SQLAlchemyError):
            return APIResponse.schema_error()

    @staticmethod
    @app.data.ServiceConfig.authentication.general_authentication_active
    def enable_2fa(user_id: str, *_args, **kwargs) -> FlaskResponse:
        """Enable 2FA for a user."""

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
                    return APIResponse.authentication_error(is_2fa_enabled = True)

            if not request.is_json or not payload:
                return APIResponse.authentication_error(is_2fa_enabled = True)
    
            code: str = payload["code"]

            try:
                otp = app.data.ServiceConfig.otp.view(user.id, OTPType.TWO_FACTOR_AUTH)

            except ValueError:
                return APIResponse.authentication_error(is_2fa_enabled = True)

            if otp.code != code:
                return APIResponse.authentication_error(is_2fa_enabled = True)

            if time.time() > otp.expires_at.timestamp():
                return APIResponse.authentication_error()

            user = app.data.ServiceConfig.user.update(user.id, UserModel.id, is_2fa_enabled = True)

            app.data.ServiceConfig.otp.delete(user.id, OTPType.TWO_FACTOR_AUTH)

            return APIResponse.success("User 2FA enabled successfully.", None, 200)
 
        except (KeyError, ValueError, ValidationError, SQLAlchemyError):
            return APIResponse.schema_error()

    @staticmethod
    @app.data.ServiceConfig.authentication.general_authentication_active
    def disable_2fa(user_id: str, *_args, **kwargs) -> FlaskResponse:
        """Disable 2FA for a user."""

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
                    return APIResponse.authentication_error(is_2fa_enabled = True)

            if not request.is_json or not payload:
                return APIResponse.authentication_error(is_2fa_enabled = True)
    
            code: str = payload["code"]

            try:
                otp = app.data.ServiceConfig.otp.view(user.id, OTPType.TWO_FACTOR_AUTH)

            except ValueError:
                return APIResponse.authentication_error(is_2fa_enabled = True)

            if otp.code != code:
                return APIResponse.authentication_error(is_2fa_enabled = True)

            if time.time() > otp.expires_at.timestamp():
                return APIResponse.authentication_error(is_2fa_enabled = True)

            user = app.data.ServiceConfig.user.update(user.id, UserModel.id, is_2fa_enabled = False)

            app.data.ServiceConfig.otp.delete(user.id, OTPType.TWO_FACTOR_AUTH)

            return APIResponse.null()
 
        except (KeyError, ValueError, ValidationError, SQLAlchemyError):
            return APIResponse.schema_error()
