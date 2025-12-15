import socketio
from app.database import get_mongo_db, SessionLocal
from app.models import User
from app.auth_utils import decode_token
from datetime import datetime
import random
import time
import asyncio
from typing import Dict
from bson import ObjectId
import json

sio = socketio.AsyncServer(cors_allowed_origins="*", async_mode="asgi")
sio_app = socketio.ASGIApp(sio)

def clean_message_for_json(msg):
    cleaned = {}
    for key, value in msg.items():
        if isinstance(value, ObjectId):
            cleaned[key] = str(value)
        elif isinstance(value, datetime):
            cleaned[key] = value.isoformat()
        elif key == '_id':
            cleaned['id'] = str(value)
        else:
            cleaned[key] = value
    if '_id' in cleaned:
        del cleaned['_id']
    return cleaned

connected_users: Dict[int, str] = {}
typing_users: Dict[int, Dict] = {}
phantom_typing_active = False
background_tasks_started = False
network_mood = "neutral"

def get_network_mood():
    global network_mood
    if random.random() < 0.05:
        network_mood = random.choice(["calm", "neutral", "restless"])
    return network_mood

def calculate_temporal_wobble():
    mood = get_network_mood()
    if mood == "calm":
        base_delay = random.uniform(0, 0.15)
        wobble_factor = random.choice([0.8, 1.0, 1.1])
    elif mood == "restless":
        base_delay = random.uniform(0.05, 0.6)
        wobble_factor = random.choice([1.0, 1.2, 1.5])
    else:
        base_delay = random.uniform(0, 0.4)
        wobble_factor = random.choice([0.9, 1.0, 1.3])
    return base_delay * wobble_factor

def should_apply_artistic_chronology():
    mood = get_network_mood()
    probability = 0.1
    if mood == "restless":
        probability = 0.2
    if mood == "calm":
        probability = 0.05
    return random.random() < probability

def get_artistic_timestamp_adjustment():
    return random.uniform(-2, 2)

async def get_user_from_token(token: str):
    payload = decode_token(token)
    if not payload:
        return None
    user_id = int(payload.get("sub"))
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        return user
    finally:
        db.close()

@sio.event
async def connect(sid, environ, auth):
    if not auth or 'token' not in auth:
        return False
    
    user = await get_user_from_token(auth['token'])
    if not user:
        return False
    
    connected_users[user.id] = sid
    await sio.emit('user_connected', {'user_id': user.id}, room=sid)
    await sio.emit('online_users', {'users': list(connected_users.keys())}, skip_sid=sid)
    return True

@sio.event
async def disconnect(sid):
    user_id = None
    for uid, socket_id in connected_users.items():
        if socket_id == sid:
            user_id = uid
            break
    
    if user_id:
        del connected_users[user_id]
        if user_id in typing_users:
            del typing_users[user_id]
        await sio.emit('user_disconnected', {'user_id': user_id}, skip_sid=sid)
        await sio.emit('online_users', {'users': list(connected_users.keys())})

@sio.event
async def send_message(sid, data):
    user = None
    for uid, socket_id in connected_users.items():
        if socket_id == sid:
            user = await get_user_from_token(data.get('token', ''))
            if user and user.id == uid:
                break
            user = None
    
    if not user:
        await sio.emit('error', {'message': 'Unauthorized'}, room=sid)
        return
    
    receiver_id = data.get('receiver_id')
    content = data.get('content')
    
    if not receiver_id or not content:
        await sio.emit('error', {'message': 'Invalid message data'}, room=sid)
        return
    
    wobble_delay = calculate_temporal_wobble()
    await asyncio.sleep(wobble_delay)
    
    mongo_db = get_mongo_db()
    timestamp = datetime.utcnow()
    
    if should_apply_artistic_chronology():
        adjustment = get_artistic_timestamp_adjustment()
        timestamp = datetime.fromtimestamp(timestamp.timestamp() + adjustment)
    
    message = {
        'sender_id': user.id,
        'receiver_id': receiver_id,
        'content': content,
        'timestamp': timestamp,
        'read': False,
        'read_at': None
    }
    
    result = mongo_db.messages.insert_one(message)
    message['id'] = str(result.inserted_id)
    message['timestamp'] = timestamp.isoformat()
    
    cleaned_message = {
        'id': message['id'],
        'sender_id': message['sender_id'],
        'receiver_id': message['receiver_id'],
        'content': message['content'],
        'timestamp': message['timestamp'],
        'read': message['read'],
        'read_at': message['read_at']
    }
    
    receiver_sid = connected_users.get(receiver_id)
    if receiver_sid:
        await sio.emit('new_message', cleaned_message, room=receiver_sid)
    
    await sio.emit('message_sent', cleaned_message, room=sid)

@sio.event
async def typing_start(sid, data):
    user = None
    for uid, socket_id in connected_users.items():
        if socket_id == sid:
            user = await get_user_from_token(data.get('token', ''))
            if user and user.id == uid:
                break
            user = None
    
    if not user:
        return
    
    receiver_id = data.get('receiver_id')
    if not receiver_id:
        return
    
    typing_users[user.id] = {
        'receiver_id': receiver_id,
        'started_at': time.time()
    }
    
    receiver_sid = connected_users.get(receiver_id)
    if receiver_sid:
        await sio.emit('user_typing', {
            'user_id': user.id,
            'is_typing': True
        }, room=receiver_sid)

@sio.event
async def typing_stop(sid, data):
    user = None
    for uid, socket_id in connected_users.items():
        if socket_id == sid:
            user = await get_user_from_token(data.get('token', ''))
            if user and user.id == uid:
                break
            user = None
    
    if not user:
        return
    
    receiver_id = data.get('receiver_id')
    if user.id in typing_users:
        del typing_users[user.id]
    
    if receiver_id:
        receiver_sid = connected_users.get(receiver_id)
        if receiver_sid:
            await sio.emit('user_typing', {
                'user_id': user.id,
                'is_typing': False
            }, room=receiver_sid)

@sio.event
async def mark_read(sid, data):
    user = None
    for uid, socket_id in connected_users.items():
        if socket_id == sid:
            user = await get_user_from_token(data.get('token', ''))
            if user and user.id == uid:
                break
            user = None
    
    if not user:
        return
    
    message_id = data.get('message_id')
    sender_id = data.get('sender_id')
    
    if not message_id:
        return
    
    mongo_db = get_mongo_db()
    try:
        message_object_id = ObjectId(message_id)
    except:
        return
    
    mongo_db.messages.update_one(
        {'_id': message_object_id, 'receiver_id': user.id},
        {'$set': {'read': True, 'read_at': datetime.utcnow()}}
    )
    
    if sender_id:
        sender_sid = connected_users.get(sender_id)
        if sender_sid:
            await sio.emit('message_read', {
                'message_id': message_id,
                'read_by': user.id,
                'read_at': datetime.utcnow().isoformat()
            }, room=sender_sid)

@sio.event
async def get_chat_history(sid, data):
    user = None
    for uid, socket_id in connected_users.items():
        if socket_id == sid:
            user = await get_user_from_token(data.get('token', ''))
            if user and user.id == uid:
                break
            user = None
    
    if not user:
        await sio.emit('error', {'message': 'Unauthorized'}, room=sid)
        return
    
    other_user_id = data.get('other_user_id')
    if not other_user_id:
        await sio.emit('error', {'message': 'Invalid user ID'}, room=sid)
        return
    
    mongo_db = get_mongo_db()
    messages = list(mongo_db.messages.find({
        '$or': [
            {'sender_id': user.id, 'receiver_id': other_user_id},
            {'sender_id': other_user_id, 'receiver_id': user.id}
        ]
    }).sort('timestamp', 1))
    
    cleaned_messages = []
    for msg in messages:
        cleaned_msg = clean_message_for_json(msg)
        if 'id' not in cleaned_msg and '_id' in msg:
            cleaned_msg['id'] = str(msg['_id'])
        cleaned_messages.append(cleaned_msg)
    
    await sio.emit('chat_history', {'messages': cleaned_messages}, room=sid)

async def phantom_typing_loop():
    while True:
        await asyncio.sleep(random.uniform(30, 120))
        if len(connected_users) >= 2 and random.random() < 0.3:
            users_list = list(connected_users.keys())
            if len(users_list) >= 2:
                phantom_user = random.choice(users_list)
                candidates = [u for u in users_list if u != phantom_user]
                if not candidates:
                    continue
                target_user = random.choice(candidates)
                target_sid = connected_users.get(target_user)
                if target_sid:
                    await sio.emit("user_typing", {"user_id": phantom_user, "is_typing": True}, room=target_sid)
                    await asyncio.sleep(random.uniform(2, 5))
                    await sio.emit("user_typing", {"user_id": phantom_user, "is_typing": False}, room=target_sid)

async def harmonic_synchronization_loop():
    while True:
        await asyncio.sleep(random.uniform(20, 60))
        if connected_users:
            phase = random.uniform(0, 1)
            mood = get_network_mood()
            await sio.emit(
                "harmonic_sync",
                {"users": list(connected_users.keys()), "phase": phase, "mood": mood}
            )

async def start_background_tasks():
    global background_tasks_started
    if background_tasks_started:
        return
    background_tasks_started = True
    asyncio.create_task(phantom_typing_loop())
    asyncio.create_task(harmonic_synchronization_loop())
