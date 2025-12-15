from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
import re

class UserCreate(BaseModel):
    mobile_number: str = Field(..., min_length=10, max_length=15)
    username: Optional[str] = None

    @field_validator('mobile_number')
    @classmethod
    def validate_mobile_number(cls, v):
        if not v:
            raise ValueError('Mobile number is required')
        
        cleaned = re.sub(r'[\s\-\(\)\+]', '', v)
        
        if not cleaned.isdigit():
            raise ValueError('Mobile number must contain only digits')
        
        if len(cleaned) < 10 or len(cleaned) > 15:
            raise ValueError('Mobile number must be between 10 and 15 digits')
        
        if cleaned.startswith('0') and len(cleaned) > 11:
            raise ValueError('Invalid mobile number format')
        
        return cleaned

class UserLogin(BaseModel):
    mobile_number: str

    @field_validator('mobile_number')
    @classmethod
    def validate_mobile_number(cls, v):
        if not v:
            raise ValueError('Mobile number is required')
        
        cleaned = re.sub(r'[\s\-\(\)\+]', '', v)
        
        if not cleaned.isdigit():
            raise ValueError('Mobile number must contain only digits')
        
        if len(cleaned) < 10 or len(cleaned) > 15:
            raise ValueError('Mobile number must be between 10 and 15 digits')
        
        return cleaned

class UserResponse(BaseModel):
    id: int
    mobile_number: str
    username: Optional[str]
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class MessageCreate(BaseModel):
    receiver_id: int
    content: str

class MessageResponse(BaseModel):
    id: str
    sender_id: int
    receiver_id: int
    content: str
    timestamp: datetime
    read: bool
    read_at: Optional[datetime] = None

class TypingIndicator(BaseModel):
    user_id: int
    is_typing: bool

