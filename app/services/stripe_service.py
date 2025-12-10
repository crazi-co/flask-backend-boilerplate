"""Service for stripe operations."""

import os
from typing import Dict, Any

import stripe
from stripe import Customer, StripeError as StripeException
from stripe.checkout import Session as CheckoutSession
from stripe.billing_portal import Session as CustomerPortalSession

from app.error_handing import StripeError



class Stripe:

    """Stripe service functions."""

    def __init__(self) -> None:
        stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

    def create_customer(self, first_name: str, last_name: str, email: str) -> Customer:
        """Creates a customer."""

        if not first_name:
            first_name = ""

        if not last_name:
            last_name = ""

        try:

            customer = stripe.Customer.create(
                name = f"{first_name} {last_name}",
                email = email
            )

            return customer
        
        except StripeException as exc:

            raise StripeError(
                self.create_customer.__name__,
                metadata = {
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                },
                original_error = exc    
            ) from exc

    def update_customer(self, customer_id: str, **kwargs) -> Customer:
        """Updates a customer."""

        try:

            data = {}

            if kwargs.get("first_name", None):
                data["name"] = f"{kwargs['first_name']} {kwargs['last_name']}"

            if kwargs.get("user_id", None):

                data["metadata"] = {
                    "user_id": kwargs["user_id"],
                }

            customer = stripe.Customer.modify(
                customer_id,
                **data
            )

            return customer
        
        except StripeException as exc:

            raise StripeError(
                self.update_customer.__name__,
                metadata = {
                    "customer_id": customer_id,
                    **kwargs,
                },
                original_error = exc    
            ) from exc

    def create_checkout_session(self, customer_id: str, price_id: str, value_in_credits: int, value_in_fiat: int, user_id: str, return_path: str) -> CheckoutSession:
        """Creates a checkout session."""

        try:

            client_url = os.getenv("CLIENT_URL")

            checkout_session = stripe.checkout.Session.create(
                customer = customer_id,
                payment_method_types = ["card"],
                line_items = [
                    {
                        "price": price_id,
                        "quantity": value_in_credits,
                    },
                ],
                mode = "payment",
                metadata = {
                    "user_id": user_id,
                    "value_in_credits": value_in_credits,
                    "value_in_fiat": value_in_fiat,
                },
                success_url = f"{client_url}/{return_path}?stripe_status=success",
                cancel_url = f"{client_url}/{return_path}?stripe_status=cancel",
                ui_mode = "hosted",
                allow_promotion_codes = True,
                billing_address_collection = "required",
                customer_update = {
                    "address": "auto",
                },
                origin_context = "web",

            )

            return checkout_session

        except StripeException as exc:

            raise StripeError(
                self.create_checkout_session.__name__,
                metadata = {
                    "customer_id": customer_id,
                    "credits": credits,
                    "user_id": user_id,
                },
                original_error = exc    
            ) from exc

    def create_customer_portal_session(self, customer_id: str) -> CustomerPortalSession:
        """Creates a customer portal session."""

        try:

            customer_portal_session = stripe.billing_portal.Session.create(
                customer = customer_id,
                return_url = os.getenv("STRIPE_RETURN_URL"),
            )

            return customer_portal_session

        except StripeException as exc:

            raise StripeError(
                self.create_customer_portal_session.__name__,
                metadata = {
                    "customer_id": customer_id,
                },
                original_error = exc    
            ) from exc

    def settle_checkout_session(self, webhook_body: str, signature: str) -> Dict[str, Any]:
        """Settles a checkout session payment."""

        try:

            event = stripe.Webhook.construct_event(
                webhook_body, signature, "whsec_FsWSXeC7H2hCIbvcvW4DL1I8bzQNBT6p"
            )

            if event.type != "checkout.session.completed":
                raise ValueError

            return event.data.object

        except StripeException as exc:

            raise StripeError(
                self.settle_checkout_session.__name__,
                metadata = {
                    "webhook_body": webhook_body,
                    "signature": signature,
                },
                original_error = exc    
            ) from exc