"""OTP database schema."""

from datetime import datetime, timezone, timedelta
from enum import Enum
import os
import secrets
import string
import uuid

from sqlalchemy import Column, DateTime, func, String, Enum as SQLAlchemyEnum, ForeignKey
from sqlmodel import SQLModel, Field



def generate_otp_id() -> str:
    """Generate an ID like otp_xxxxxxxx."""

    return f"otp_{uuid.uuid4().hex}"

def generate_otp_code() -> str:
    """Generate an OTP code."""

    return "".join(secrets.choice(string.digits) for _ in range(6))

def generate_otp_expiry() -> datetime:
    """Generate an OTP expiry."""

    return datetime.now(timezone.utc) + timedelta(minutes = int(os.getenv("OTP_EXPIRY_IN_MINUTES")))

class OTPType(str, Enum):
    """OTP type."""

    ACTIVATION = "ACTIVATION"
    TWO_FACTOR_AUTH = "TWO_FACTOR_AUTH"
    CHANGE_PASSWORD = "CHANGE_PASSWORD"

class OTP(SQLModel, table = True):
    """OTP model."""

    __tablename__ = "otps"

    id: str = Field(
        default_factory = generate_otp_id,
        min_length = 36,
        max_length = 36,
        sa_column = Column(String(36), primary_key = True)
    )
    user_id: str = Field(
        min_length = 37,
        max_length = 37,
        sa_column = Column(String(37), ForeignKey("users.id", ondelete = "CASCADE"), index = True, nullable = False)
    )
    code: str = Field(
        default_factory = generate_otp_code,
        min_length = 6,
        max_length = 6,
        sa_column = Column(String(6), nullable = False)
    )
    type: OTPType = Field(
        sa_column = Column(SQLAlchemyEnum(OTPType, name = "otp_type"), nullable = False)
    )
    expires_at: datetime = Field(
        default_factory = generate_otp_expiry,
        sa_column = Column(DateTime(timezone = True), nullable = False)
    )
    created_at: datetime = Field(
        default_factory = lambda: datetime.now(timezone.utc),
        sa_column = Column(
            DateTime(timezone = True),
            server_default = func.now(), # pylint: disable = E1102
            nullable = False
        )
    )
    updated_at: datetime = Field(
        default_factory = lambda: datetime.now(timezone.utc),
        sa_column = Column(
            DateTime(timezone = True),
            server_default = func.now(), # pylint: disable = E1102
            onupdate = func.now(), # pylint: disable = E1102
            nullable = False
        )
    )
