"""
Project-related Pydantic schemas for request/response serialization.
"""

import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List

from pydantic import BaseModel, Field


class ProjectBase(BaseModel):
    """Base project schema with common fields."""
    
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    is_public: bool = False
    metadata_: Optional[Dict[str, Any]] = Field(default_factory=dict, alias="metadata")
    settings: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ProjectCreate(ProjectBase):
    """Schema for project creation."""
    
    giraffe_project_id: Optional[str] = None
    giraffe_model_url: Optional[str] = None


class ProjectUpdate(BaseModel):
    """Schema for project updates."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    is_public: Optional[bool] = None
    is_active: Optional[bool] = None
    metadata_: Optional[Dict[str, Any]] = Field(None, alias="metadata")
    settings: Optional[Dict[str, Any]] = None
    giraffe_project_id: Optional[str] = None
    giraffe_model_url: Optional[str] = None


class ProjectResponse(ProjectBase):
    """Schema for project responses."""
    
    id: uuid.UUID
    owner_id: uuid.UUID
    is_active: bool
    giraffe_project_id: Optional[str] = None
    giraffe_model_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class LayerBase(BaseModel):
    """Base layer schema with common fields."""
    
    name: str = Field(..., min_length=1, max_length=255)
    layer_type: str = Field(..., min_length=1, max_length=50)
    is_visible: bool = True
    is_locked: bool = False
    z_index: int = 0
    style: Optional[Dict[str, Any]] = Field(default_factory=dict)
    properties: Optional[Dict[str, Any]] = Field(default_factory=dict)


class LayerCreate(LayerBase):
    """Schema for layer creation."""
    
    geometry: Optional[str] = None
    giraffe_object_id: Optional[str] = None


class LayerUpdate(BaseModel):
    """Schema for layer updates."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    layer_type: Optional[str] = Field(None, min_length=1, max_length=50)
    is_visible: Optional[bool] = None
    is_locked: Optional[bool] = None
    z_index: Optional[int] = None
    geometry: Optional[str] = None
    style: Optional[Dict[str, Any]] = None
    properties: Optional[Dict[str, Any]] = None
    giraffe_object_id: Optional[str] = None


class LayerResponse(LayerBase):
    """Schema for layer responses."""
    
    id: uuid.UUID
    project_id: uuid.UUID
    geometry: Optional[str] = None
    giraffe_object_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class EditHistoryResponse(BaseModel):
    """Schema for edit history responses."""
    
    id: uuid.UUID
    project_id: uuid.UUID
    user_id: uuid.UUID
    action: str
    object_type: str
    object_id: Optional[uuid.UUID] = None
    changes: Optional[Dict[str, Any]] = None
    previous_data: Optional[Dict[str, Any]] = None
    new_data: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None
    created_at: datetime
    
    model_config = {"from_attributes": True}


class ProjectListResponse(BaseModel):
    """Schema for paginated project list responses."""
    
    projects: List[ProjectResponse]
    total: int
    page: int
    size: int
    pages: int


class LayerListResponse(BaseModel):
    """Schema for layer list responses."""
    
    layers: List[LayerResponse]
    total: int