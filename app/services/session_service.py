"""Service for session operations."""

from datetime import datetime, timedelta, timezone
import os
from typing import Dict, Any, List, Optional

from sqlmodel import select, Session as SQLModelSession
import jwt

import app.data
from app.schemas import Session as SessionModel
from app.services import Database



class Session:
    """Session service functions."""

    def __init__(self) -> None:
        self.database_service = Database(SessionModel)

    def create(
        self,
        user_id: str
    ) -> SessionModel:
        """Create a session."""
        
        session = self.database_service.view(user_id, SessionModel.user_id)

        expiry = datetime.now(timezone.utc) + timedelta(days = int(os.getenv("SESSION_EXPIRY_IN_DAYS")))

        payload: Dict[str, Any] = {
            "sub": user_id,
            "role": os.getenv("USER_ROLE"),
            "iat": datetime.now(timezone.utc).timestamp(),
            "exp": expiry.timestamp(),
        }

        token = jwt.encode(
            payload,
            os.getenv("JWT_SECRET_KEY"),
            algorithm = os.getenv("JWT_ALGORITHM")
        )
        
        session = SessionModel.model_validate({
            "user_id": user_id,
            "token": f"crazi_couser_{token}",
            "expires_at": expiry,
        })

        return self.database_service.insert(session)

    def view_all(
        self,
        user_id: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[SessionModel]:
        """View all sessions."""

        if not limit and not offset:

            with SQLModelSession(app.data.engine) as session:  # pylint: disable=E1129

                statement = select(SessionModel).where(SessionModel.user_id == user_id).offset(offset).limit(limit)
                sessions = session.exec(statement).all()
                
                return sessions

        sessions = []
        offset = 0

        while True:

            with SQLModelSession(app.data.engine) as session:  # pylint: disable=E1129

                statement = select(SessionModel).where(SessionModel.user_id == user_id).offset(offset).limit(limit)
                results = session.exec(statement).all()

            sessions.extend(results)

            offset += limit

            if len(results) < 100:
                break

        return sessions

    def view(self, value: str, column: str) -> SessionModel:
        """View a session."""

        if (
            column != SessionModel.id and
            column != SessionModel.token and
            column != SessionModel.user_id
        ):
            raise ValueError

        session = self.database_service.view(value, column)

        if session is None:
            print(value, column)
            raise ValueError
        
        return session
    
    def delete(self, value: str, column: str) -> None:
        """Delete a session."""

        if (
            column != SessionModel.id and
            column != SessionModel.token and
            column != SessionModel.user_id
        ):
            raise ValueError

        session = self.database_service.view(value, column)

        if session is None:
            raise ValueError

        return self.database_service.delete(session)
