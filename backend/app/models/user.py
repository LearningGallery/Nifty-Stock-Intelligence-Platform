"""
User Data Models
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user model"""
    email: EmailStr
    name: Optional[str] = None


class UserCreate(UserBase):
    """User creation model"""
    password: str = Field(..., min_length=8)


class UserResponse(UserBase):
    """User response model"""
    user_id: str
    created_at: datetime
    email_verified: bool = False
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "user@example.com",
                "name": "John Doe",
                "created_at": "2024-01-15T10:30:00Z",
                "email_verified": True
            }
        }


class UserUpdate(BaseModel):
    """User update model"""
    name: Optional[str] = None
    email: Optional[EmailStr] = None


class PasswordChange(BaseModel):
    """Password change model"""
    old_password: str
    new_password: str = Field(..., min_length=8)
