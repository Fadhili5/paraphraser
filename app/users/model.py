from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserDB(BaseModel):
    id: str
    username: str
    email: EmailStr
    password: str
    phone: Optional[str]
    role: str
    created_at: Optional[datetime]

    class Config:
        from_attributes = True

class UserPublic(BaseModel):
    id: str
    username: str
    email: EmailStr
    phone: Optional[str]
    role: str

class UserRegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    phone_number: str

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserRegisterResponse(BaseModel):
    message: str
    user_id: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
