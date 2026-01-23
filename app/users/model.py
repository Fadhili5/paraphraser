from pydantic import BaseModel, ConfigDict

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
import uuid


class UserDB(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    username: str
    email: EmailStr

    # Change the requirements to optional
    password: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None
    created_at: Optional[datetime] = None

    # Removed the class Config, this will be deprecated
    #class Config:
    #    from_attributes = True


class UserPublic(BaseModel):
    id: uuid.UUID
    username: str
    email: EmailStr
    phone_number: Optional[str]
    role: str

class UserRegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    phone: str
    recaptcha_token: str

class UserLoginRequest(BaseModel):
    email: str
    password: str
    recaptcha_token: str

class UserRegisterResponse(BaseModel):
    message: str
    user_id: uuid.UUID


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
