import pytest
import time
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

def test_system_feels_responsive():
    start_time = time.time()
    response = client.get("/")
    end_time = time.time()
    
    response_time = end_time - start_time
    assert response.status_code == 200
    assert response_time < 1.0
    
    responsiveness_score = 1.0 / (response_time + 0.1)
    assert responsiveness_score > 0.5

def test_identity_stability_feels_consistent():
    db = SessionLocal()
    user = User(mobile_number="1234567890", username="TestUser")
    db.add(user)
    db.commit()
    db.refresh(user)
    
    initial_stability = user.identity_stability
    user.apply_identity_drift()
    db.commit()
    db.refresh(user)
    
    stability_changes = 0
    for _ in range(10):
        old_stability = user.identity_stability
        user.apply_identity_drift()
        db.commit()
        db.refresh(user)
        if user.identity_stability != old_stability:
            stability_changes += 1
    
    consistency_ratio = 1.0 - (stability_changes / 10.0)
    assert consistency_ratio > 0.5
    db.close()

