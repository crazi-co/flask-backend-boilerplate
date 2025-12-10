"""Service for authentication operations."""

import base64
from functools import wraps
import os
import time
from typing import Callable, List

import bcrypt
from flask import request, Response as FlaskResponse
import jwt
from jwt.exceptions import DecodeError

import app.data
from app.schemas import User as UserModel, Session as SessionModel
from app.utils.api_responses import APIResponse



class Authentication:
    """Authentication service functions."""

    def __init__(self) -> None:
        pass

    def validate_jwt(self, token: str) -> UserModel:
        """Validate a JWT token."""
        
        payload = jwt.decode(token, os.getenv("JWT_SECRET_KEY"), [os.getenv("JWT_ALGORITHM")])

        if payload["role"] == os.getenv("USER_ROLE"):

            token = "crazi_couser_" + token
            session = app.data.ServiceConfig.session.view(token, SessionModel.token)

            if time.time() > session.expires_at.timestamp():
                raise ValueError
        
        return app.data.ServiceConfig.user.view(session.user_id, UserModel.id)
    
    def general_authentication_inactive(self, route: Callable) -> Callable:
        """General authentication decorator for user and private authentication."""

        @wraps(route)
        def authenticator(*args, **kwargs) -> FlaskResponse:
            
            try:

                authorization: str = request.headers[os.getenv("AUTHORIZATION_HEADER")]

                if authorization == os.getenv("PRIVATE_API_KEY"):
                    role = os.getenv("PRIVATE_ROLE")

                else:

                    authorization: List[str] = authorization.split(" ")

                    if authorization[0] != "Bearer":
                        raise ValueError

                    elif authorization[1].startswith("crazi_couser_"):

                        token = authorization[1].replace("crazi_couser_", "")
                        role = os.getenv("USER_ROLE")
                        
                    else:
                        raise ValueError

                    user = self.validate_jwt(token)

                    kwargs["token"] = authorization[1]
                    kwargs["user"] = user

                kwargs["role"] = role
                    
            except (KeyError, ValueError, DecodeError):
                return APIResponse.authentication_error()
            
            return route(*args, **kwargs)
        
        return authenticator

    def general_authentication_active(self, route: Callable) -> Callable:
        """General authentication decorator for active user and private authentication."""

        @wraps(route)
        def authenticator(*args, **kwargs) -> FlaskResponse:
            
            try:

                authorization: str = request.headers[os.getenv("AUTHORIZATION_HEADER")]

                if authorization == os.getenv("PRIVATE_API_KEY"):
                    role = os.getenv("PRIVATE_ROLE")

                else:

                    authorization: List[str] = authorization.split(" ")

                    if authorization[0] != "Bearer":
                        raise ValueError

                    elif authorization[1].startswith("crazi_couser_"):

                        token = authorization[1].replace("crazi_couser_", "")
                        role = os.getenv("USER_ROLE")
                        
                    else:
                        raise ValueError

                    user = self.validate_jwt(token)

                    if (
                        not user.is_active or
                        not user.first_name or
                        not user.last_name
                    ):
                        return APIResponse.user_inactive_error()

                    kwargs["token"] = authorization[1]
                    kwargs["user"] = user

                kwargs["role"] = role
                    
            except (KeyError, ValueError, DecodeError):
                return APIResponse.authentication_error()
            
            return route(*args, **kwargs)
        
        return authenticator

    def static_authentication(self, route: Callable) -> Callable:
        """Static authentication decorator for only public and private authentication."""

        @wraps(route)
        def authenticator(*args, **kwargs) -> FlaskResponse:
            
            try:
                authorization: str = request.headers[os.getenv("AUTHORIZATION_HEADER")]

                if authorization == os.getenv("PRIVATE_API_KEY"):
                    role = os.getenv("PRIVATE_ROLE")

                elif authorization == os.getenv("PUBLIC_API_KEY"):
                    role = os.getenv("PUBLIC_ROLE")

                else:
                    raise ValueError
                
                kwargs["role"] = role

            except (KeyError, ValueError):
                return APIResponse.authentication_error()
            
            return route(*args, **kwargs)
        
        return authenticator

    def private_authentication(self, route: Callable) -> Callable:
        """Private authentication decorator for only private authentication."""

        @wraps(route)
        def authenticator(*args, **kwargs) -> FlaskResponse:
            
            try:

                authorization: str = request.headers[os.getenv("AUTHORIZATION_HEADER")]

                if authorization != os.getenv("PRIVATE_API_KEY"):
                    raise ValueError
                
                kwargs["role"] = os.getenv("PRIVATE_ROLE")

            except (KeyError, ValueError):
                return APIResponse.authentication_error()
            
            return route(*args, **kwargs)
        
        return authenticator

    def basic_authentication(self, route: Callable) -> Callable:
        """Basic authentication decorator for only user authentication with email and password."""

        @wraps(route)
        def authenticator(*args, **kwargs) -> FlaskResponse:
            try:
                authorization: str = request.headers[os.getenv("AUTHORIZATION_HEADER")]

                token = authorization.split(" ")

                if token[0] != "Basic":
                    raise ValueError
                
                credentials = base64.b64decode(token[1].encode("utf8")).decode("utf8").split(":")

                user = app.data.ServiceConfig.user.view(credentials[0], UserModel.email)

                if not bcrypt.checkpw(credentials[1].encode("utf8"), user.password.encode("utf8")):
                    raise ValueError

                token = app.data.ServiceConfig.session.create(user.id).token

                kwargs["user"] = user
                kwargs["token"] = token
                kwargs["password"] = credentials[1]
                
            except (KeyError, ValueError):

                return APIResponse.authentication_error()
            
            return route(*args, **kwargs)
        
        return authenticator
