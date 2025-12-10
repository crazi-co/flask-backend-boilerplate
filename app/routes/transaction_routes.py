"""Routes for transaction operations."""

import os

from flask import request, Response as FlaskResponse
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

import app.data
from app.schemas import User as UserModel
from app.schemas.database.transaction import TransactionType
from app.utils.api_responses import APIResponse



class TransactionRoute:

    """Transaction route functions."""

    @staticmethod
    @app.data.ServiceConfig.authentication.general_authentication_active
    def view_all(user_id: str, *_args, **kwargs) -> FlaskResponse:
        """View all transactions."""

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

            limit: int = int(request.args.get("limit", None))
            offset: int = int(request.args.get("offset", None))

            transactions = [transaction.model_dump() for transaction in app.data.ServiceConfig.transaction.view_all(user_id, limit, offset)]

            for i, _ in enumerate(transactions):
                del transactions[i]["stripe_payment_intent"]

            return APIResponse.success("Transactions fetched successfully.", transactions, 200)
 
        except (TypeError, ValueError):
            return APIResponse.schema_error()

    @staticmethod
    @app.data.ServiceConfig.authentication.general_authentication_active
    def view(user_id: str, transaction_id: str, *_args, **kwargs) -> FlaskResponse:
        """View a transaction."""

        role = kwargs["role"]

        if (
            role == os.getenv("USER_ROLE") or
            role == os.getenv("API_KEY_ROLE")
        ):

            user: UserModel = kwargs["user"]

            if user.id != user_id:
                return APIResponse.resource_access_error()

        try:
            transaction = app.data.ServiceConfig.transaction.view(transaction_id, user_id)

        except ValueError:
            return APIResponse.resource_presence_error("Transaction")

        transaction = transaction.model_dump()
        del transaction["stripe_payment_intent"]

        return APIResponse.success("Transaction fetched successfully.", transaction, 200)

    @staticmethod
    @app.data.ServiceConfig.authentication.private_authentication
    def create(user_id: str, *_args, **_kwargs) -> FlaskResponse:
        """Create a transaction."""

        try:

            try:
                app.data.ServiceConfig.user.view(user_id, UserModel.id)

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
    
            description: str = payload["description"]
            value_in_credits: float = round(float(payload["value_in_credits"]), 2)
            value_in_fiat: float = round(float(payload["value_in_fiat"]), 2)
            transaction_type: TransactionType = payload["type"]

            try:
                transaction = app.data.ServiceConfig.transaction.create(user_id, description, value_in_credits, value_in_fiat, transaction_type)
            
            except ValidationError as exc:
                raise ValueError from exc

            transaction = transaction.model_dump()

            return APIResponse.success("Transaction created successfully.", transaction, 201)
 
        except (KeyError, ValueError, ValidationError, SQLAlchemyError):
            return APIResponse.schema_error()

    @staticmethod
    @app.data.ServiceConfig.authentication.private_authentication
    def update(user_id: str, transaction_id: str, *_args, **_kwargs) -> FlaskResponse:
        """Update a transaction."""

        try:

            try:
                app.data.ServiceConfig.user.view(user_id, UserModel.id)

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
    
            forbidden_keys = ["id", "created_at", "updated_at"]

            for key in payload.keys():

                if key in forbidden_keys:
                    raise ValueError

            if "value_in_credits" in payload:
                payload["value_in_credits"] = round(float(payload["value_in_credits"]), 2)

            if "value_in_fiat" in payload:
                payload["value_in_fiat"] = round(float(payload["value_in_fiat"]), 2)

            try:
                transaction = app.data.ServiceConfig.transaction.update(transaction_id, user_id, **payload)

            except ValidationError as exc:
                raise ValueError from exc

            except ValueError:
                return APIResponse.resource_presence_error("Transaction")

            transaction = transaction.model_dump()

            return APIResponse.success("Transaction updated successfully.", transaction, 200)
 
        except (KeyError, ValueError, ValidationError, SQLAlchemyError):
            return APIResponse.schema_error()

    @staticmethod
    @app.data.ServiceConfig.authentication.private_authentication
    def delete(user_id: str, transaction_id: str, *_args, **_kwargs) -> FlaskResponse:
        """Delete a transaction."""

        try:
            app.data.ServiceConfig.user.view(user_id, UserModel.id)

        except ValueError:
            return APIResponse.resource_presence_error("User")

        try:
            app.data.ServiceConfig.transaction.delete(transaction_id, user_id)
        
        except ValueError:
            return APIResponse.resource_presence_error("Transaction")

        return APIResponse.null()
