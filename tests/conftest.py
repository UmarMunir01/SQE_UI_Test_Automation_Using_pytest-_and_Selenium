"""Shared isolated Flask and Selenium fixtures for the assignment suite."""

import pytest

from app import create_app
from app.db import db
from app.services.user_service import UserService


@pytest.fixture
def app(tmp_path, monkeypatch):
    """Create a fresh application database for each test."""
    database_path = (tmp_path / "todolist.sqlite").as_posix()
    monkeypatch.setenv("DB_NAME", database_path)
    monkeypatch.setenv("KEY", "sqe-test-secret")

    test_app = create_app()
    test_app.config.update(TESTING=True, SECRET_KEY="sqe-test-secret")
    with test_app.app_context():
        db.drop_all()
        db.create_all()
        yield test_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def user_factory(app):
    """Create users through the same validation and persistence service as the app."""
    counter = 0

    def create_user(username=None, email=None, password="Strong123"):
        nonlocal counter
        counter += 1
        username = username or f"testuser{counter}"
        email = email or f"{username}@example.com"
        result = UserService.create_user(email, username, password, password)
        assert result["success"], result
        return result["user"]

    return create_user
