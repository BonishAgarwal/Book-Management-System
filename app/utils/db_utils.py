from app import db
from sqlalchemy.exc import SQLAlchemyError
from contextlib import asynccontextmanager

# Asynchronous context manager for database sessions
@asynccontextmanager
async def db_session():
    """Provides a transactional scope for database operations."""
    async with db.session() as session:
        try:
            yield session
            await session.commit()
        except SQLAlchemyError as e:
            await session.rollback()
            print(f"Error: {e}")
            raise
        finally:
            await session.close()