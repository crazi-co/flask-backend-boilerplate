"""Service for transaction operations."""

from typing import List, Optional
from sqlmodel import select, Session, desc

import app.data
from app.schemas import Transaction as TransactionModel
from app.schemas.database.transaction import TransactionType
from app.services import Database



class Transaction:
    """Transaction service functions."""

    def __init__(self) -> None:
        self.database_service = Database(TransactionModel)

    def view(self, transaction_id: str, user_id: str) -> TransactionModel:
        """View a transaction."""

        with Session(app.data.engine) as session:  # pylint: disable=E1129

            statement = select(TransactionModel).where(TransactionModel.id == transaction_id).where(TransactionModel.user_id == user_id)
            transaction = session.exec(statement).first()

        if transaction is None:
            raise ValueError
        
        return transaction
    
    def view_all(
        self,
        user_id: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[TransactionModel]:
        """View all transactions."""

        if not limit and not offset:

            with Session(app.data.engine) as session:  # pylint: disable=E1129

                statement = select(TransactionModel).where(TransactionModel.user_id == user_id).order_by(desc(TransactionModel.created_at)).offset(offset).limit(limit)
                transactions = session.exec(statement).all()
                
                return transactions

        transactions = []
        offset = 0

        while True:

            with Session(app.data.engine) as session:  # pylint: disable=E1129

                statement = select(TransactionModel).where(TransactionModel.user_id == user_id).order_by(desc(TransactionModel.created_at)).offset(offset).limit(limit)
                results = session.exec(statement).all()

            transactions.extend(results)

            offset += limit

            if len(results) < 100:
                break

        return transactions

    def create(
        self,
        user_id: str,
        payment_intent: str,
        description: str,
        value_in_credits: float,
        value_in_fiat: float,
        transaction_type: TransactionType
    ) -> TransactionModel:
        """Create a transaction."""

        transaction = TransactionModel.model_validate({
            "user_id": user_id,
            "stripe_payment_intent": payment_intent,
            "description": description,
            "value_in_credits": value_in_credits,
            "value_in_fiat": value_in_fiat,
            "type": transaction_type,
        })

        return self.database_service.insert(transaction)

    def update(self, transaction_id: str, user_id: str, **kwargs) -> TransactionModel:
        """Update a transaction."""

        with Session(app.data.engine) as session:  # pylint: disable=E1129

            statement = select(TransactionModel).where(TransactionModel.id == transaction_id).where(TransactionModel.user_id == user_id)
            transaction = session.exec(statement).first()

        if transaction is None:
            raise ValueError

        for key, value in kwargs.items():

            try:
                setattr(transaction, key, value)

            except ValueError as exc:
                raise KeyError from exc

        return self.database_service.update(TransactionModel.model_validate(transaction.model_dump()))

    def delete(self, transaction_id: str, user_id: str) -> None:
        """Delete a transaction."""

        with Session(app.data.engine) as session:  # pylint: disable=E1129

            statement = select(TransactionModel).where(TransactionModel.id == transaction_id).where(TransactionModel.user_id == user_id)
            transaction = session.exec(statement).first()

        if transaction is None:
            raise ValueError

        return self.database_service.delete(transaction)
