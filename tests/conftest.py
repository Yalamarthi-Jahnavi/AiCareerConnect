"""
Pytest Fixtures (conftest.py)
===============================
Shared test fixtures available to ALL test files.

WHY THIS FILE EXISTS:
    Pytest automatically loads conftest.py and makes its fixtures
    available to every test file in the directory. This avoids
    duplicating setup code (app creation, test client, test DB)
    across test files.
"""

import pytest
from app import create_app
from app.extensions import db as _db
from app.models.user import User


@pytest.fixture(scope='session')
def app():
    """Create the Flask application with testing configuration."""
    app = create_app('testing')
    with app.app_context():
        _db.create_all()
    yield app
    with app.app_context():
        _db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """Create a test client for making HTTP requests."""
    return app.test_client()


@pytest.fixture(scope='function')
def db_session(app):
    """Provide a clean database session for each test."""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.rollback()
        _db.drop_all()


@pytest.fixture
def sample_user(db_session):
    """Create a sample user for testing."""
    user = User(
        username='testuser',
        email='test@example.com',
        full_name='Test User',
        role='job_seeker',
    )
    user.set_password('TestPass123')
    db_session.session.add(user)
    db_session.session.commit()
    return user


@pytest.fixture
def sample_employer(db_session):
    """Create a sample employer for testing."""
    user = User(
        username='testemployer',
        email='employer@example.com',
        full_name='Test Employer',
        role='employer',
    )
    user.set_password('TestPass123')
    db_session.session.add(user)
    db_session.session.commit()
    return user


@pytest.fixture
def auth_headers(client, sample_user):
    """Get JWT auth headers for a logged-in user."""
    response = client.post('/api/auth/login', json={
        'email': 'test@example.com',
        'password': 'TestPass123',
    })
    token = response.get_json()['access_token']
    return {'Authorization': f'Bearer {token}'}
