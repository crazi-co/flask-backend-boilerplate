"""Transaction database schema."""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional
import uuid

from sqlalchemy import Column, DateTime, func, String, Float, Enum as SQLAlchemyEnum, ForeignKey
from sqlmodel import SQLModel, Field



def generate_transaction_id() -> str:
    """Generate an ID like user_xxxxxxxx."""

    return f"transaction_{uuid.uuid4().hex}"


class TransactionType(str, Enum):
    """Transaction type."""

    CREDIT = "CREDIT"
    DEBIT = "DEBIT"


class Transaction(SQLModel, table = True):
    """Transaction model."""

    __tablename__ = "transactions"

    id: str = Field(
        default_factory = generate_transaction_id,
        min_length = 44,
        max_length = 44,
        sa_column = Column(String(44), primary_key = True)
    )
    user_id: str = Field(
        min_length = 37,
        max_length = 37,
        sa_column = Column(String(37), ForeignKey("users.id", ondelete = "CASCADE"), index = True, nullable = False)
    )
    stripe_payment_intent: Optional[str] = Field(
        sa_column = Column(String(255),
        index = True,
        unique = True,
        nullable = True)
    )
    description: str = Field(
        sa_column = Column(String(512), nullable = False)
    )
    value_in_credits: float = Field(
        sa_column = Column(Float, nullable = False)
    )
    value_in_fiat: float = Field(
        sa_column = Column(Float, nullable = False)
    )
    type: TransactionType = Field(
        sa_column = Column(SQLAlchemyEnum(TransactionType, name = "transaction_type"), nullable = False)
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
