import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal, engine, Base
from app.models import User

client = TestClient(app)

@pytest.fixture(scope="function", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_register_user():
    response = client.post(
        "/api/auth/register",
        json={"mobile_number": "1234567890", "username": "TestUser"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["mobile_number"] == "1234567890"
    assert data["username"] == "TestUser"
    assert "id" in data

def test_register_duplicate_mobile():
    client.post(
        "/api/auth/register",
        json={"mobile_number": "1234567890", "username": "TestUser"}
    )
    response = client.post(
        "/api/auth/register",
        json={"mobile_number": "1234567890", "username": "AnotherUser"}
    )
    assert response.status_code == 400

def test_login_user():
    client.post(
        "/api/auth/register",
        json={"mobile_number": "1234567890", "username": "TestUser"}
    )
    response = client.post(
        "/api/auth/login",
        json={"mobile_number": "1234567890"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_mobile():
    response = client.post(
        "/api/auth/login",
        json={"mobile_number": "9999999999"}
    )
    assert response.status_code == 401

def test_register_invalid_mobile_format():
    response = client.post(
        "/api/auth/register",
        json={"mobile_number": "123", "username": "TestUser"}
    )
    assert response.status_code == 422

def test_register_mobile_with_special_chars():
    response = client.post(
        "/api/auth/register",
        json={"mobile_number": "123-456-7890", "username": "TestUser"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["mobile_number"] == "1234567890"

def test_register_mobile_non_digits():
    response = client.post(
        "/api/auth/register",
        json={"mobile_number": "12345abc678", "username": "TestUser"}
    )
    assert response.status_code == 422

def test_login_mobile_validation():
    response = client.post(
        "/api/auth/login",
        json={"mobile_number": "12345"}
    )
    assert response.status_code == 422

