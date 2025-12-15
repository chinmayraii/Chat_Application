import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal, engine, Base
from app.models import User
from app.auth_utils import create_access_token

client = TestClient(app)

@pytest.fixture(scope="function", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def auth_token():
    db = SessionLocal()
    user = User(mobile_number="1234567890", username="TestUser")
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token(data={"sub": str(user.id), "mobile": user.mobile_number})
    db.close()
    return token

def test_get_current_user(auth_token):
    response = client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["mobile_number"] == "1234567890"

def test_get_current_user_unauthorized():
    response = client.get("/api/users/me")
    assert response.status_code == 403

def test_list_users(auth_token):
    db = SessionLocal()
    user2 = User(mobile_number="0987654321", username="User2")
    db.add(user2)
    db.commit()
    db.close()
    
    response = client.get(
        "/api/users/",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1

