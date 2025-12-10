"""User database schema."""

from datetime import datetime, timezone
from typing import Optional
import uuid

from pydantic import EmailStr
from sqlalchemy import Column, DateTime, func, String, Float, Boolean
from sqlmodel import SQLModel, Field



def generate_user_id() -> str:
    """Generate an ID like user_xxxxxxxx."""

    return f"user_{uuid.uuid4().hex}"


class User(SQLModel, table = True):
    """User model."""

    __tablename__ = "users"

    id: str = Field(
        default_factory = generate_user_id,
        min_length = 37,
        max_length = 37,
        sa_column = Column(String(37), primary_key = True)
    )
    first_name: Optional[str] = Field(
        sa_column = Column(String(255),
        nullable = True)
    )
    last_name: Optional[str] = Field(
        sa_column = Column(String(255),
        nullable = True)
    )
    email: EmailStr = Field(
        sa_column = Column(String(255),
        index = True,
        unique = True,
        nullable = False)
    )
    stripe_customer_id: str = Field(
        sa_column = Column(String(255),
        index = True,
        unique = True,
        nullable = False)
    )
    google_user_id: Optional[str] = Field(
        sa_column = Column(String(255),
        index = True,
        unique = True,
        nullable = True)
    )
    password: str = Field(
        min_length = 60,
        max_length = 60,
        sa_column = Column(String(60), nullable = False)
    )
    credits: float = Field(
        default = 100,
        sa_column = Column(Float, nullable = False)
    )
    is_2fa_enabled: bool = Field(
        default = False,
        sa_column = Column(Boolean, nullable = False)
    )
    is_dark_mode: bool = Field(
        default = True,
        sa_column = Column(Boolean, nullable = False)
    )
    is_active: bool = Field(
        default = False,
        sa_column = Column(Boolean, nullable = False)
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
