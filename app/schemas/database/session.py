"""Session database schema."""

from datetime import datetime, timezone
import uuid

from sqlalchemy import Column, DateTime, func, String, ForeignKey
from sqlmodel import SQLModel, Field



def generate_session_id() -> str:
    """Generate an ID like session_xxxxxxxx."""

    return f"session_{uuid.uuid4().hex}"

class Session(SQLModel, table = True):
    """Session model."""

    __tablename__ = "sessions"

    id: str = Field(
        default_factory = generate_session_id,
        min_length = 40,
        max_length = 40,
        sa_column = Column(String(40), primary_key = True)
    )
    user_id: str = Field(
        min_length = 37,
        max_length = 37,
        sa_column = Column(String(37), ForeignKey("users.id", ondelete = "CASCADE"), index = True, nullable = False)
    )
    token: str = Field(
        sa_column = Column(String(512), index = True, unique = True, nullable = False)
    )
    expires_at: datetime = Field(
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
