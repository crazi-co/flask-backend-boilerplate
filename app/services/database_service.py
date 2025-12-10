"""Service for database operations."""

import os
from typing import Optional, List
from sqlmodel import create_engine, select, SQLModel, Session as SQLModelSession
from sqlalchemy import inspect

import app.data



class Database:
    """Database service functions."""

    def __init__(self, table: SQLModel) -> None:
        self.table = table

    @staticmethod
    def initialize() -> None:
        """Initialize the database."""
        
        if not app.data.engine:
            app.data.engine = create_engine(os.getenv("DATABASE_DSN"), echo = True)

        if app.data.table_creation_required:

            existing_tables = inspect(app.data.engine).get_table_names()

            if not existing_tables:
                SQLModel.metadata.create_all(app.data.engine)

            app.data.table_creation_required = False

    def insert(self, model: SQLModel) -> SQLModel:
        """Insert a model into the database."""

        with SQLModelSession(app.data.engine) as session:  # pylint: disable=E1129

            session.add(model)
            session.commit()
            session.refresh(model)

            return model

    def view(self, value: str, column: Optional[str] = None) -> Optional[SQLModel]:
        """View a model from the database."""

        if column is None:
            column = self.table.id

        with SQLModelSession(app.data.engine) as session:  # pylint: disable=E1129

            statement = select(self.table).where(column == value)
            result = session.exec(statement).first()

            return result

    def view_all(self, limit: int = 100, offset: int = 0) -> List[SQLModel]:
        """View all models from the database."""

        with SQLModelSession(app.data.engine) as session:  # pylint: disable=E1129

            statement = select(self.table).offset(offset).limit(limit)
            results = session.exec(statement).all()
            return results

    def update(self, model: SQLModel) -> SQLModel:
        """Update a model from the database."""

        with SQLModelSession(app.data.engine) as session:  # pylint: disable=E1129

            session.merge(model)
            session.commit()

            return model

    def delete(self, model: SQLModel) -> None:
        """Delete a model from the database."""

        with SQLModelSession(app.data.engine) as session:  # pylint: disable=E1129

            session.delete(model)
            session.commit()
