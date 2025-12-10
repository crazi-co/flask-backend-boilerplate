"""Data package for the app."""

import os
from typing import TYPE_CHECKING

from sqlalchemy import Engine

if TYPE_CHECKING:

    from app.services import (
        Authentication,
        Email,
        OTP,
        Session,
        Transaction,
        User,
        Stripe
    )



engine: Engine = None
table_creation_required: bool = True

credits_rate = [{
    "lower_limit": 5,
    "upper_limit": 10000,
    "rate": 100,
    "stripe_price_id": os.getenv("STRIPE_PRICE_ID"),
}]


class ServiceConfig:
    """Service configuration."""

    authentication: "Authentication" = None
    email: "Email" = None
    otp: "OTP" = None
    stripe: "Stripe" = None
    session: "Session" = None
    transaction: "Transaction" = None
    user: "User" = None
