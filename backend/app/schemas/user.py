from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    profile_picture: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class UserResponse(UserBase):
    id: int
    profile_picture: Optional[str] = None
    created_at: datetime
    last_login: Optional[datetime] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class PersonalAdBase(BaseModel):
    content: str
    latitude: float
    longitude: float

class PersonalAdCreate(PersonalAdBase):
    pass

class PersonalAdUpdate(BaseModel):
    content: Optional[str] = None
    is_active: Optional[bool] = None

class PersonalAdResponse(PersonalAdBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    is_active: bool

class MessageBase(BaseModel):
    content: str

class MessageCreate(MessageBase):
    receiver_id: int

class MessageResponse(MessageBase):
    id: int
    sender_id: int
    receiver_id: int
    created_at: datetime
    is_read: bool
    read_at: Optional[datetime] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
