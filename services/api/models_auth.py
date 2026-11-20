from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserRole(str, Enum):
    admin = "admin"
    manager = "manager"
    user = "user"


class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=1, max_length=200)
    role: UserRole = UserRole.user


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=1, max_length=200)
    password: str = Field(min_length=8, max_length=128)
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    phone: Optional[str] = None
    address: Optional[str] = None


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    role: Optional[UserRole] = None
    password: Optional[str] = Field(default=None, min_length=8, max_length=128)


class UserResponse(UserBase):
    id: int
    created_at: datetime


class ProfileBase(BaseModel):
    user_id: int
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    phone: Optional[str] = None
    address: Optional[str] = None


class ProfileResponse(ProfileBase):
    id: int
    updated_at: datetime


class ProfileMeResponse(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class AuthMeResponse(BaseModel):
    email: EmailStr
    role: UserRole
    profile: Optional[ProfileMeResponse] = None
