# tests/test_auth_routes.py
import os
import sys
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.database import Base, get_db
from app.main import create_app
from app.db import models


load_dotenv(".env.test")

TEST_DB_FILE = "./test_auth.db"
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


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    if os.path.exists(TEST_DB_FILE):
        os.remove(TEST_DB_FILE)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    if os.path.exists(TEST_DB_FILE):
        os.remove(TEST_DB_FILE)


def test_register_success():
    email = "test_register@example.com"
    password = "StrongPass123"
    response = client.post("/auth/register", json={"email": email, "password": password})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert isinstance(data["access_token"], str)

def test_register_existing_user():
    # Vider la table
    with next(override_get_db()) as db:
        db.query(models.User).delete()
        db.commit()

    email = "duplicate@example.com"
    password = "ValidPass123"  # mot de passe valide selon la policy

    # 1er registre → doit passer
    response1 = client.post("/auth/register", json={"email": email, "password": password})
    assert response1.status_code == 200

    # 2e registre → doit échouer pour doublon
    response2 = client.post("/auth/register", json={"email": email, "password": password})
    assert response2.status_code == 400
    assert response2.json()["detail"] == "Email already registered"


def test_login_success():
    email = "loginuser@example.com"
    password = "MyPass123"
    client.post("/auth/register", json={"email": email, "password": password})
    response = client.post("/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_invalid_credentials():
    response = client.post("/auth/login", json={"email": "loginuser@example.com", "password": "WrongPass123"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


def test_forgot_password_existing_user():
    email = "reset@example.com"
    password = "ResetPass123"
    client.post("/auth/register", json={"email": email, "password": password})

    # Patch correct
    with patch("app.auth_routes.set_reset_token") as mock_set_token:
        mock_set_token.return_value = "mockedtoken123"
        response = client.post("/auth/forgot-password", json={"email": email})
        assert response.status_code == 200
        data = response.json()
        assert "reset_token" in data
        assert data["reset_token"] == "mockedtoken123"


def test_forgot_password_unknown_user():
    response = client.post("/auth/forgot-password", json={"email": "unknown@example.com"})
    assert response.status_code == 200
    data = response.json()
    assert data["message"].startswith("If an account")
