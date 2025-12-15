import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal, engine, Base, get_mongo_db
from app.models import User
from app.auth_utils import create_access_token
from datetime import datetime

client = TestClient(app)

@pytest.fixture(scope="function", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    mongo_db = get_mongo_db()
    yield
    Base.metadata.drop_all(bind=engine)
    mongo_db.messages.delete_many({})

@pytest.fixture
def auth_token():
    db = SessionLocal()
    user = User(mobile_number="1234567890", username="TestUser")
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token(data={"sub": str(user.id), "mobile": user.mobile_number})
    db.close()
    return token, user.id

@pytest.fixture
def second_user():
    db = SessionLocal()
    user = User(mobile_number="0987654321", username="User2")
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user.id

def test_get_chat_history_empty(auth_token, second_user, setup_database):
    token, user_id = auth_token
    mongo_db = get_mongo_db()
    mongo_db.messages.delete_many({
        '$or': [
            {'sender_id': user_id, 'receiver_id': second_user},
            {'sender_id': second_user, 'receiver_id': user_id}
        ]
    })
    response = client.get(
        f"/api/messages/history/{second_user}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0

def test_get_chat_history_with_messages(auth_token, second_user, setup_database):
    token, user_id = auth_token
    
    mongo_db = get_mongo_db()
    mongo_db.messages.delete_many({
        '$or': [
            {'sender_id': user_id, 'receiver_id': second_user},
            {'sender_id': second_user, 'receiver_id': user_id}
        ]
    })
    
    message = {
        'sender_id': user_id,
        'receiver_id': second_user,
        'content': 'Test message',
        'timestamp': datetime.utcnow(),
        'read': False,
        'read_at': None
    }
    mongo_db.messages.insert_one(message)
    
    response = client.get(
        f"/api/messages/history/{second_user}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    test_messages = [msg for msg in data if msg['content'] == 'Test message']
    assert len(test_messages) >= 1
    assert test_messages[0]['sender_id'] == user_id
    assert test_messages[0]['receiver_id'] == second_user

def test_get_chat_history_unauthorized():
    response = client.get("/api/messages/history/1")
    assert response.status_code == 403

def test_get_chat_history_marks_messages_as_read(auth_token, second_user):
    token, user_id = auth_token
    
    mongo_db = get_mongo_db()
    message = {
        'sender_id': second_user,
        'receiver_id': user_id,
        'content': 'Unread message',
        'timestamp': datetime.utcnow(),
        'read': False,
        'read_at': None
    }
    result = mongo_db.messages.insert_one(message)
    
    response = client.get(
        f"/api/messages/history/{second_user}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    
    updated_message = mongo_db.messages.find_one({'_id': result.inserted_id})
    assert updated_message['read'] == True
    assert updated_message['read_at'] is not None

