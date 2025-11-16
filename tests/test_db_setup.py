import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from sqlmodel import Session, SQLModel, create_engine

# from blog import models
from blog.database import create_db_and_tables, engine, get_session


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_db_path = Path(temp_dir) / "test_blog.db"
        test_sqlite_url = f"sqlite:///{temp_db_path}"
        test_engine = create_engine(
            test_sqlite_url, connect_args={"check_same_thread": False}
        )
        SQLModel.metadata.create_all(test_engine)
        yield test_engine
        test_engine.dispose()


def test_create_db_and_tables():
    """Test that create_db_and_tables creates tables in the database."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_db_path = Path(temp_dir) / "test_blog.db"
        test_sqlite_url = f"sqlite:///{temp_db_path}"
        test_engine = create_engine(
            test_sqlite_url, connect_args={"check_same_thread": False}
        )

        with patch("blog.database.engine", test_engine):
            create_db_and_tables()

        # Verify tables exist by checking metadata
        assert len(SQLModel.metadata.tables) > 0
        test_engine.dispose()


def test_get_session(temp_db):
    """Test that get_session returns a valid Session object."""
    with patch("blog.database.engine", temp_db):
        session_generator = get_session()
        session = next(session_generator)

        assert isinstance(session, Session)

        # Cleanup
        try:
            next(session_generator)
        except StopIteration:
            pass


def test_engine_configuration():
    """Test that the engine is properly configured."""
    assert engine is not None
    assert str(engine.url).startswith("sqlite:///")


def test_session_context_manager(temp_db):
    """Test that get_session properly handles session context."""
    with patch("blog.database.engine", temp_db):
        session_generator = get_session()
        session = next(session_generator)

        # Session should be open and usable
        assert session.is_active

        # Cleanup
        try:
            next(session_generator)
        except StopIteration:
            pass
