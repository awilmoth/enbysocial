import pytest
from fastapi.testclient import TestClient
from peewee import SqliteDatabase
from contextlib import contextmanager

from app.main import app
from app.models.user import User, PersonalAd, Message
from app.database import db, database_state_default, database_state, PeeweeConnectionState

# Use SQLite for testing
test_db = SqliteDatabase(':memory:')
MODELS = [User, PersonalAd, Message]

@pytest.fixture(autouse=True)
def setup_test_db():
    # Connect to test database and create tables
    test_db.bind(MODELS, bind_refs=False, bind_backrefs=False)
    test_db.connect()
    test_db.create_tables(MODELS)

    # Setup test state and yield for tests
    state = PeeweeConnectionState()
    database_state.set(state)
    
    yield
    
    # Cleanup after tests
    test_db.drop_tables(MODELS)
    test_db.close()

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def test_user():
    user = User.create(
        username="testuser",
        email="test@example.com",
        password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LHHWsDzZ7GZm3nFm2"  # password: testpass
    )
    return user

@pytest.fixture
def test_user_token(client, test_user):
    response = client.post(
        "/users/token",
        data={
            "username": "testuser",
            "password": "testpass"
        }
    )
    return response.json()["access_token"]

@pytest.fixture
def authorized_client(client, test_user_token):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {test_user_token}"
    }
    return client
