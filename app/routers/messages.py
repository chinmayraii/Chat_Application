from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db, get_mongo_db
from app.models import User
from app.schemas import MessageResponse
from app.routers.users import get_current_user
from datetime import datetime
from typing import List

router = APIRouter()

@router.get("/history/{other_user_id}", response_model=List[MessageResponse])
async def get_chat_history(
    other_user_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    mongo_db = get_mongo_db()
    
    messages = list(mongo_db.messages.find({
        '$or': [
            {'sender_id': current_user.id, 'receiver_id': other_user_id},
            {'sender_id': other_user_id, 'receiver_id': current_user.id}
        ]
    }).sort('timestamp', 1).skip(skip).limit(limit))
    
    mongo_db.messages.update_many(
        {
            'sender_id': other_user_id,
            'receiver_id': current_user.id,
            'read': False
        },
        {
            '$set': {
                'read': True,
                'read_at': datetime.utcnow()
            }
        }
    )
    
    result = []
    for msg in messages:
        result.append(MessageResponse(
            id=str(msg['_id']),
            sender_id=msg['sender_id'],
            receiver_id=msg['receiver_id'],
            content=msg['content'],
            timestamp=msg['timestamp'],
            read=msg.get('read', False),
            read_at=msg.get('read_at')
        ))
    
    return result

