import os
import sys
import pytest
from uuid import uuid4
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Allow import from app directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.database import Base, get_db
from app.main import create_app

load_dotenv(".env.test")

# ==========================================================
# Setup SQLite test database
# ==========================================================
TEST_DB_FILE = "./test_user.db"
SQLALCHEMY_DATABASE_URL = f"sqlite:///{TEST_DB_FILE}"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app = create_app()
app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


# ==========================================================
# Fixtures
# ==========================================================
@pytest.fixture(scope="module", autouse=True)
def setup_db():
    """Create a temporary test database before tests, and clean it up after."""
    if os.path.exists(TEST_DB_FILE):
        os.remove(TEST_DB_FILE)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    if os.path.exists(TEST_DB_FILE):
        os.remove(TEST_DB_FILE)


# ==========================================================
# CRUD User Tests
# ==========================================================
def test_create_user_success():
    """✅ Create a valid user profile"""
    payload = {
        "auth_id": str(uuid4()),
        "email": "jean@example.com",
        "first_name": "Jean",
        "last_name": "Dupont"
    }
    response = client.post("/users/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["first_name"] == "Jean"
    assert data["email"] == "jean@example.com"


def test_create_user_duplicate():
    """❌ Prevent creating a profile with an existing auth_id"""
    auth_id = str(uuid4())
    payload = {"auth_id": auth_id, "email": "test@example.com", "first_name": "Test"}
    client.post("/users/", json=payload)
    response = client.post("/users/", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "User profile already exists."


def test_get_user_success():
    """✅ Retrieve an existing user"""
    payload = {"auth_id": str(uuid4()), "email": "alice@example.com", "first_name": "Alice"}
    create_response = client.post("/users/", json=payload)
    assert create_response.status_code == 201
    user_id = create_response.json()["id"]

    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["email"] == "alice@example.com"


def test_get_user_not_found():
    """❌ Attempt to access a non-existent user"""
    fake_id = str(uuid4())
    response = client.get(f"/users/{fake_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found."


def test_update_user_success():
    """✅ Successfully update an existing user"""
    # 1️⃣ Create user
    auth_id = str(uuid4())
    payload = {
        "auth_id": auth_id,
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe"
    }
    response_create = client.post("/users/", json=payload)
    assert response_create.status_code == 201
    user_id = response_create.json()["id"]

    # 2️⃣ Update user
    response_update = client.patch(f"/users/{user_id}", json={"first_name": "Johnny"})
    assert response_update.status_code == 201
    data = response_update.json()
    assert data["first_name"] == "Johnny"
    assert data["email"] == "john@example.com"


def test_update_user_not_found():
    """❌ Try updating a non-existent user"""
    fake_id = str(uuid4())
    response = client.patch(f"/users/{fake_id}", json={"first_name": "Ghost"})
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found."


def test_check_profile_status_complete():
    """✅ Verify that a complete profile returns is_complete=True"""
    payload = {
        "auth_id": str(uuid4()),
        "email": "sara@example.com",
        "first_name": "Sara",
        "last_name": "Kone"
    }
    create_response = client.post("/users/", json=payload)
    assert create_response.status_code == 201
    user_id = create_response.json()["id"]

    response = client.get(f"/users/{user_id}/status")
    assert response.status_code == 200
    assert response.json()["is_complete"] is True


def test_check_profile_status_incomplete():
    """✅ Verify that a partial profile returns is_complete=False"""
    payload = {"auth_id": str(uuid4()), "email": "ben@example.com", "first_name": "Ben"}
    create_response = client.post("/users/", json=payload)
    assert create_response.status_code == 201
    user_id = create_response.json()["id"]

    response = client.get(f"/users/{user_id}/status")
    assert response.status_code == 200
    assert response.json()["is_complete"] is False
