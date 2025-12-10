"""Service for otp operations."""

from sqlmodel import select, Session

import app.data
from app.schemas import OTP as OTPModel
from app.schemas.database.otp import OTPType
from app.services import Database



class OTP:
    """OTP service functions."""

    def __init__(self) -> None:
        self.database_service = Database(OTPModel)

    def create(
        self,
        user_id: str,
        otp_type: OTPType
    ) -> OTPModel:
        """Create a otp."""
        
        with Session(app.data.engine) as session:  # pylint: disable=E1129

            statement = select(OTPModel).where(OTPModel.user_id == user_id).where(OTPModel.type == otp_type)
            otp = session.exec(statement).first()

        if otp is not None:
            self.database_service.delete(otp)
        
        otp = OTPModel.model_validate({
            "user_id": user_id,
            "type": otp_type,
        })

        return self.database_service.insert(otp)

    def view(self, user_id: str, otp_type: OTPType) -> OTPModel:
        """View a otp."""

        with Session(app.data.engine) as session:  # pylint: disable=E1129

            statement = select(OTPModel).where(OTPModel.user_id == user_id).where(OTPModel.type == otp_type)
            otp = session.exec(statement).first()

        if otp is None:
            raise ValueError
        
        return otp
    
    def delete(self, user_id: str, otp_type: OTPType) -> None:
        """Delete a otp."""

        with Session(app.data.engine) as session:  # pylint: disable=E1129

            statement = select(OTPModel).where(OTPModel.user_id == user_id).where(OTPModel.type == otp_type)
            otp = session.exec(statement).first()

        if otp is None:
            raise ValueError

        return self.database_service.delete(otp)
