"""Service for user operations."""

from typing import List, Optional

import bcrypt

import app.data
from app.schemas import User as UserModel
from app.schemas.database.transaction import TransactionType, Transaction as TransactionModel
from app.services import Database



class User:
    """User service functions."""

    def __init__(self) -> None:
        self.database_service = Database(UserModel)

    def create(
        self,
        first_name: str,
        last_name: str,
        email: str,
        password: str,
        google_user_id: Optional[str] = None,
        is_active: bool = False
    ) -> UserModel:
        """Create a user."""
        
        user = self.database_service.view(email, UserModel.email)

        if user:
            raise ValueError

        if first_name:
            first_name = " ".join(word.capitalize() for word in first_name.split(" "))

        if last_name:
            last_name = " ".join(word.capitalize() for word in last_name.split(" "))

        stripe_customer = app.data.ServiceConfig.stripe.create_customer(first_name, last_name, email)
        
        user = UserModel.model_validate({
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "stripe_customer_id": stripe_customer.id,
            "password": bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8"),
            "google_user_id": google_user_id,
            "is_active": is_active,
        })

        user: UserModel = self.database_service.insert(user)

        app.data.ServiceConfig.stripe.update_customer(stripe_customer.id, user_id = user.id)

        app.data.ServiceConfig.transaction.create(user.id, None, "Free credits on signup.", 100, 1, TransactionType.CREDIT)

        return user

    def view(self, value: str, column: str) -> UserModel:
        """View a user."""

        if column != UserModel.id and column != UserModel.email:
            raise ValueError

        user = self.database_service.view(value, column)

        if user is None:
            raise ValueError
        
        return user
    
    def view_all(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[UserModel]:
        """View all users."""

        if not limit and not offset:
            return self.database_service.view_all(limit, offset)

        users = []
        offset = 0

        while True:

            results = self.database_service.view_all(offset = offset)

            users.extend(results)

            offset += limit

            if len(results) < 100:
                break

        return users

    def update(self, value: str, column: str, **kwargs) -> UserModel:
        """Update a user."""

        if column != UserModel.id and column != UserModel.email:
            raise ValueError

        user = self.database_service.view(value, column)

        if user is None:
            raise ValueError

        stripe_data = {}

        for key, value in kwargs.items():

            try:

                if key == "first_name" or key == "last_name":

                    value = " ".join(word.capitalize() for word in value.split(" "))

                setattr(user, key, value)

            except ValueError as exc:
                raise KeyError from exc

        if "first_name" in kwargs:
            stripe_data["first_name"] = kwargs["first_name"]
        
        if "last_name" in kwargs:
            stripe_data["last_name"] = kwargs["last_name"]
        
        if stripe_data:
            app.data.ServiceConfig.stripe.update_customer(user.stripe_customer_id, **stripe_data)

        return self.database_service.update(UserModel.model_validate(user.model_dump()))

    def delete(self, value: str, column: str) -> None:
        """Delete a user."""

        # delete whatever was dependent on the user

        if column != UserModel.id and column != UserModel.email:
            raise ValueError

        user = self.database_service.view(value, column)

        if user is None:
            raise ValueError

        return self.database_service.delete(user)

    def update_credits(self, value: str, column: str, user_credits: float, payment_intent: Optional[str] = None, transaction_description: Optional[str] = None, transaction_type: Optional[TransactionType] = None) -> TransactionModel:
        """Update a user's credits."""

        if column != UserModel.id and column != UserModel.email:
            raise ValueError

        user: UserModel = self.database_service.view(value, column)

        if user is None:
            raise ValueError

        if transaction_type == TransactionType.CREDIT:
            user_credits += user.credits
            
        elif transaction_type == TransactionType.DEBIT:
            user_credits -= user.credits

        credits_difference = user_credits - user.credits
        credits_difference_absolute = abs(credits_difference)

        if not transaction_description:
            transaction_description = f"Admin updated credits from {user.credits} to {user_credits}."

        user.credits = user_credits

        user = self.database_service.update(UserModel.model_validate(user.model_dump()))

        applicable_credits_rate = [rate for rate in app.data.credits_rate if rate["lower_limit"] <= credits_difference_absolute <= rate["upper_limit"]]

        if applicable_credits_rate:
            value_in_fiat = credits_difference_absolute / applicable_credits_rate[0]["rate"]

        else:
            value_in_fiat = credits_difference_absolute / 100

        credits_difference_absolute = round(credits_difference_absolute, 2)
        value_in_fiat = round(value_in_fiat, 2)

        return app.data.ServiceConfig.transaction.create(
            user.id,
            payment_intent,
            transaction_description,
            credits_difference_absolute,
            value_in_fiat,
            TransactionType.CREDIT if credits_difference > 0 else TransactionType.DEBIT
        )
