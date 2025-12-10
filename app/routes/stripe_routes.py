"""Routes for stripe operations."""

import os

from flask import request, Response as FlaskResponse
from pydantic import ValidationError

import app.data
from app.schemas.database.transaction import TransactionType
from app.schemas import User as UserModel
from app.utils.api_responses import APIResponse



class StripeRoute:

    """Stripe route functions."""

    @staticmethod
    @app.data.ServiceConfig.authentication.general_authentication_active
    def rate(*_args, **_kwargs) -> FlaskResponse:
        """View credits rate."""

        return APIResponse.success("Credits rate fetched successfully. Upper limit and lower limit are in fiat. Rate is in credits per dollar. Any amount beyond the limits will not be credited.", app.data.credits_rate, 200)

    @staticmethod
    @app.data.ServiceConfig.authentication.general_authentication_active
    def portal(*_args, **kwargs) -> FlaskResponse:
        """Create a customer portal session for a user."""

        if (
            kwargs["role"] != os.getenv("USER_ROLE") and
            kwargs["role"] != os.getenv("API_KEY_ROLE")
        ):
            return APIResponse.resource_access_error()

        user: UserModel = kwargs["user"]

        customer_portal_session = app.data.ServiceConfig.stripe.create_customer_portal_session(user.stripe_customer_id)

        customer_portal_session = {
            "url": customer_portal_session.url,
        }

        return APIResponse.success("Customer portal session created successfully.", customer_portal_session, 201)

    @staticmethod
    @app.data.ServiceConfig.authentication.general_authentication_active
    def buy(*_args, **kwargs) -> FlaskResponse:
        """Buy credits."""

        try:

            if (
                kwargs["role"] != os.getenv("USER_ROLE") and
                kwargs["role"] != os.getenv("API_KEY_ROLE")
            ):
                return APIResponse.resource_access_error()

            user: UserModel = kwargs["user"]

            try:
                payload = request.json
                
            except Exception as exc: # pylint: disable = W0718

                if request.is_json:
                    raise ValueError from exc

                else:
                    return APIResponse.empty_body_error()

            if not request.is_json or not payload:
                return APIResponse.empty_body_error()

            amount: int = int(payload["amount"])
            return_path = payload["return_path"]

            applicable_credits_rate = [rate for rate in app.data.credits_rate if rate["lower_limit"] <= amount <= rate["upper_limit"]]

            if not applicable_credits_rate:
                return APIResponse.credits_rate_not_found_error()

            value_in_credits = applicable_credits_rate[0]["rate"] * amount
            checkout_session = app.data.ServiceConfig.stripe.create_checkout_session(user.stripe_customer_id, applicable_credits_rate[0]["stripe_price_id"], value_in_credits, amount, user.id, return_path)

            checkout_session = {
                "return_path": return_path,
                "url": checkout_session.url,
                "value_in_credits": value_in_credits,
                "value_in_fiat": amount,
            }

            return APIResponse.success("Checkout session created successfully.", checkout_session, 201)
 
        except (KeyError, ValueError):
            return APIResponse.schema_error()

    @staticmethod
    def settle(*_args, **_kwargs) -> FlaskResponse:
        """Settle a checkout session payment."""

        try:

            try:
                event_data = app.data.ServiceConfig.stripe.settle_checkout_session(request.data, request.headers["Stripe-Signature"])

            except ValueError:
                return APIResponse.schema_error()

            try:

                value_in_fiat = float(event_data["metadata"]["value_in_fiat"])
                value_in_credits = float(event_data["metadata"]["value_in_credits"])

                app.data.ServiceConfig.user.update_credits(
                    event_data["metadata"]["user_id"],
                    UserModel.id,
                    value_in_credits,
                    payment_intent = event_data["payment_intent"],
                    transaction_description = f"User bought {value_in_credits} credits for ${value_in_fiat}.",
                    transaction_type = TransactionType.CREDIT
                )

            except ValidationError as exc:
                raise ValueError from exc
                
            return APIResponse.success("Checkout session settled successfully.", None, 200)
 
        except (KeyError, ValueError):
            return APIResponse.schema_error()
