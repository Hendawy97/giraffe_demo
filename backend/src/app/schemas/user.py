"""
User-related Pydantic schemas for request/response serialization.
"""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema with common fields."""
    
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = Field(None, max_length=255)
    is_active: bool = True
    is_verified: bool = False


class UserCreate(BaseModel):
    """Schema for user creation."""
    
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=100)
    full_name: Optional[str] = Field(None, max_length=255)


class UserUpdate(BaseModel):
    """Schema for user updates."""
    
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    """Schema for user responses."""
    
    id: uuid.UUID
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    is_active: bool
    is_verified: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class UserLogin(BaseModel):
    """Schema for user login."""
    
    username: str = Field(..., description="Username or email")
    password: str = Field(..., min_length=1)


class Token(BaseModel):
    """Schema for authentication tokens."""
    
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """Schema for token data."""
    
    username: Optional[str] = None
    user_id: Optional[uuid.UUID] = None