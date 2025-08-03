"""
Project-related models for Giraffe SDK integration.
"""

import uuid
from typing import Optional, Dict, Any

from sqlalchemy import String, Text, Boolean, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from geoalchemy2 import Geometry

from app.db.session import Base
from app.models.base import UUIDMixin, TimestampMixin


class Project(Base, UUIDMixin, TimestampMixin):
    """Project model for managing Giraffe projects."""
    
    __tablename__ = "projects"
    
    # Basic project information
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    # Project ownership
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    
    # Project status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Giraffe integration
    giraffe_project_id: Mapped[Optional[str]] = mapped_column(String(255), index=True)
    giraffe_model_url: Mapped[Optional[str]] = mapped_column(Text)
    
    # Project metadata
    metadata_: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        "metadata", 
        JSON, 
        default=dict
    )
    
    # Project settings
    settings: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON, 
        default=dict
    )
    
    # Relationships
    layers = relationship("Layer", back_populates="project", cascade="all, delete-orphan")
    edit_history = relationship("EditHistory", back_populates="project", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Project(id={self.id}, name={self.name}, owner_id={self.owner_id})>"


class Layer(Base, UUIDMixin, TimestampMixin):
    """Layer model for organizing geometric objects within projects."""
    
    __tablename__ = "layers"
    
    # Layer identification
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    layer_type: Mapped[str] = mapped_column(String(50), nullable=False)  # wall, floor, roof, etc.
    
    # Project relationship
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id"),
        nullable=False,
        index=True,
    )
    
    # Layer properties
    is_visible: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_locked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    z_index: Mapped[int] = mapped_column(default=0, nullable=False)
    
    # Geometric data
    geometry: Mapped[Optional[str]] = mapped_column(Geometry("GEOMETRY"))
    
    # Layer styling and properties
    style: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, default=dict)
    properties: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, default=dict)
    
    # Giraffe integration
    giraffe_object_id: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Relationships
    project = relationship("Project", back_populates="layers")
    
    def __repr__(self) -> str:
        return f"<Layer(id={self.id}, name={self.name}, type={self.layer_type}, project_id={self.project_id})>"


class EditHistory(Base, UUIDMixin, TimestampMixin):
    """Edit history model for tracking changes to projects."""
    
    __tablename__ = "edit_history"
    
    # Edit identification
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id"),
        nullable=False,
        index=True,
    )
    
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    
    # Edit details
    action: Mapped[str] = mapped_column(String(50), nullable=False)  # create, update, delete
    object_type: Mapped[str] = mapped_column(String(50), nullable=False)  # layer, project, etc.
    object_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))
    
    # Change data
    changes: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    previous_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    new_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    
    # Session information
    session_id: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Relationships
    project = relationship("Project", back_populates="edit_history")
    
    def __repr__(self) -> str:
        return f"<EditHistory(id={self.id}, action={self.action}, object_type={self.object_type}, project_id={self.project_id})>"