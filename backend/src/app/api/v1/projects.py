"""
Project management API endpoints for Giraffe SDK integration.
"""

import uuid
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.project import Project, Layer, EditHistory
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectListResponse,
    LayerCreate,
    LayerUpdate,
    LayerResponse,
    LayerListResponse,
    EditHistoryResponse,
)


router = APIRouter()


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Create a new project.
    
    Args:
        project_data: Project creation data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        ProjectResponse: Created project data
    """
    db_project = Project(
        name=project_data.name,
        description=project_data.description,
        is_public=project_data.is_public,
        metadata_=project_data.metadata_,
        settings=project_data.settings,
        giraffe_project_id=project_data.giraffe_project_id,
        giraffe_model_url=project_data.giraffe_model_url,
        owner_id=current_user.id,
    )
    
    db.add(db_project)
    await db.commit()
    await db.refresh(db_project)
    
    return db_project


@router.get("/", response_model=ProjectListResponse)
async def get_projects(
    skip: int = Query(0, ge=0, description="Number of projects to skip"),
    limit: int = Query(50, ge=1, le=100, description="Number of projects to return"),
    search: str = Query(None, description="Search term for project name or description"),
    public_only: bool = Query(False, description="Return only public projects"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get projects list with pagination and filtering.
    
    Args:
        skip: Number of projects to skip
        limit: Number of projects to return
        search: Search term for filtering
        public_only: Whether to return only public projects
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        ProjectListResponse: Paginated list of projects
    """
    # Base query
    query = select(Project).where(Project.is_active == True)
    
    # Apply filters
    if public_only:
        query = query.where(Project.is_public == True)
    else:
        # Show user's own projects and public projects
        query = query.where(
            or_(
                Project.owner_id == current_user.id,
                Project.is_public == True
            )
        )
    
    if search:
        query = query.where(
            or_(
                Project.name.ilike(f"%{search}%"),
                Project.description.ilike(f"%{search}%")
            )
        )
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Get projects with pagination
    query = query.offset(skip).limit(limit).order_by(Project.updated_at.desc())
    result = await db.execute(query)
    projects = result.scalars().all()
    
    return ProjectListResponse(
        projects=projects,
        total=total,
        page=skip // limit + 1,
        size=limit,
        pages=(total + limit - 1) // limit,
    )


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get project by ID.
    
    Args:
        project_id: Project ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        ProjectResponse: Project data
        
    Raises:
        HTTPException: If project not found or no access
    """
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check access permissions
    if not project.is_public and project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this project"
        )
    
    return project


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: uuid.UUID,
    project_update: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Update project by ID.
    
    Args:
        project_id: Project ID
        project_update: Project update data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        ProjectResponse: Updated project data
        
    Raises:
        HTTPException: If project not found or no permissions
    """
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Only owner can update project
    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this project"
        )
    
    # Update project fields
    update_data = project_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "metadata_":
            setattr(project, "metadata_", value)
        else:
            setattr(project, field, value)
    
    await db.commit()
    await db.refresh(project)
    
    return project


@router.delete("/{project_id}")
async def delete_project(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Delete project by ID.
    
    Args:
        project_id: Project ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        dict: Deletion success message
        
    Raises:
        HTTPException: If project not found or no permissions
    """
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Only owner can delete project
    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete this project"
        )
    
    # Soft delete
    project.is_active = False
    await db.commit()
    
    return {"message": "Project deleted successfully"}


# Layer endpoints
@router.get("/{project_id}/layers", response_model=LayerListResponse)
async def get_project_layers(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get all layers for a project.
    
    Args:
        project_id: Project ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        LayerListResponse: List of project layers
    """
    # Check project access
    await get_project(project_id, current_user, db)
    
    result = await db.execute(
        select(Layer)
        .where(Layer.project_id == project_id)
        .order_by(Layer.z_index.asc(), Layer.created_at.desc())
    )
    layers = result.scalars().all()
    
    return LayerListResponse(layers=layers, total=len(layers))


@router.post("/{project_id}/layers", response_model=LayerResponse, status_code=status.HTTP_201_CREATED)
async def create_layer(
    project_id: uuid.UUID,
    layer_data: LayerCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Create a new layer in a project.
    
    Args:
        project_id: Project ID
        layer_data: Layer creation data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        LayerResponse: Created layer data
    """
    # Check project access and ownership
    project = await get_project(project_id, current_user, db)
    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to create layers in this project"
        )
    
    db_layer = Layer(
        project_id=project_id,
        name=layer_data.name,
        layer_type=layer_data.layer_type,
        is_visible=layer_data.is_visible,
        is_locked=layer_data.is_locked,
        z_index=layer_data.z_index,
        geometry=layer_data.geometry,
        style=layer_data.style,
        properties=layer_data.properties,
        giraffe_object_id=layer_data.giraffe_object_id,
    )
    
    db.add(db_layer)
    await db.commit()
    await db.refresh(db_layer)
    
    return db_layer


@router.put("/{project_id}/layers/{layer_id}", response_model=LayerResponse)
async def update_layer(
    project_id: uuid.UUID,
    layer_id: uuid.UUID,
    layer_update: LayerUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Update a layer in a project.
    
    Args:
        project_id: Project ID
        layer_id: Layer ID
        layer_update: Layer update data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        LayerResponse: Updated layer data
    """
    # Check project access and ownership
    project = await get_project(project_id, current_user, db)
    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update layers in this project"
        )
    
    result = await db.execute(
        select(Layer).where(
            and_(Layer.id == layer_id, Layer.project_id == project_id)
        )
    )
    layer = result.scalar_one_or_none()
    
    if not layer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Layer not found"
        )
    
    # Update layer fields
    update_data = layer_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(layer, field, value)
    
    await db.commit()
    await db.refresh(layer)
    
    return layer


@router.delete("/{project_id}/layers/{layer_id}")
async def delete_layer(
    project_id: uuid.UUID,
    layer_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Delete a layer from a project.
    
    Args:
        project_id: Project ID
        layer_id: Layer ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        dict: Deletion success message
    """
    # Check project access and ownership
    project = await get_project(project_id, current_user, db)
    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete layers in this project"
        )
    
    result = await db.execute(
        select(Layer).where(
            and_(Layer.id == layer_id, Layer.project_id == project_id)
        )
    )
    layer = result.scalar_one_or_none()
    
    if not layer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Layer not found"
        )
    
    await db.delete(layer)
    await db.commit()
    
    return {"message": "Layer deleted successfully"}


@router.get("/{project_id}/history", response_model=List[EditHistoryResponse])
async def get_project_history(
    project_id: uuid.UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get edit history for a project.
    
    Args:
        project_id: Project ID
        skip: Number of history entries to skip
        limit: Number of history entries to return
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List[EditHistoryResponse]: List of edit history entries
    """
    # Check project access
    await get_project(project_id, current_user, db)
    
    result = await db.execute(
        select(EditHistory)
        .where(EditHistory.project_id == project_id)
        .order_by(EditHistory.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    history = result.scalars().all()
    
    return history