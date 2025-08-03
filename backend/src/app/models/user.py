"""
User model for authentication and user management.
"""

from typing import Optional

from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.models.base import UUIDMixin, TimestampMixin


class User(Base, UUIDMixin, TimestampMixin):
    """User model for authentication and authorization."""
    
    __tablename__ = "users"
    
    # User identification
    email: Mapped[str] = mapped_column(
        String(255), 
        unique=True, 
        index=True, 
        nullable=False
    )
    username: Mapped[str] = mapped_column(
        String(100), 
        unique=True, 
        index=True, 
        nullable=False
    )
    
    # User profile
    full_name: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Authentication
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # User status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Giraffe integration
    giraffe_user_id: Mapped[Optional[str]] = mapped_column(String(255))
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, username={self.username})>"