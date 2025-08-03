"""
Demo API endpoints that work without database.
"""

import uuid
from typing import Any, List, Dict
from datetime import datetime

from fastapi import APIRouter
from pydantic import BaseModel


router = APIRouter()


class DemoProject(BaseModel):
    """Demo project model."""
    id: str
    name: str
    description: str
    created_at: str
    layers_count: int
    is_public: bool


class DemoLayer(BaseModel):
    """Demo layer model."""
    id: str
    name: str
    layer_type: str
    is_visible: bool
    geometry_type: str


# Mock data for demo
DEMO_PROJECTS = [
    DemoProject(
        id=str(uuid.uuid4()),
        name="Sample Building Model",
        description="A demo 3D building model with multiple floors",
        created_at=datetime.now().isoformat(),
        layers_count=5,
        is_public=True,
    ),
    DemoProject(
        id=str(uuid.uuid4()),
        name="Urban Planning Layout",
        description="City block layout with buildings and infrastructure",
        created_at=datetime.now().isoformat(),
        layers_count=8,
        is_public=True,
    ),
    DemoProject(
        id=str(uuid.uuid4()),
        name="Interior Design Office",
        description="Modern office interior with furniture and fixtures",
        created_at=datetime.now().isoformat(),
        layers_count=12,
        is_public=False,
    ),
]

DEMO_LAYERS = {
    DEMO_PROJECTS[0].id: [
        DemoLayer(
            id=str(uuid.uuid4()),
            name="Foundation",
            layer_type="structure",
            is_visible=True,
            geometry_type="solid",
        ),
        DemoLayer(
            id=str(uuid.uuid4()),
            name="Walls",
            layer_type="wall",
            is_visible=True,
            geometry_type="surface",
        ),
        DemoLayer(
            id=str(uuid.uuid4()),
            name="Windows",
            layer_type="opening",
            is_visible=True,
            geometry_type="surface",
        ),
        DemoLayer(
            id=str(uuid.uuid4()),
            name="Roof",
            layer_type="structure",
            is_visible=True,
            geometry_type="surface",
        ),
        DemoLayer(
            id=str(uuid.uuid4()),
            name="Electrical",
            layer_type="system",
            is_visible=False,
            geometry_type="line",
        ),
    ]
}


@router.get("/projects", response_model=List[DemoProject])
async def get_demo_projects() -> Any:
    """
    Get demo projects.
    
    Returns:
        List[DemoProject]: List of demo projects
    """
    return DEMO_PROJECTS


@router.get("/projects/{project_id}", response_model=DemoProject)
async def get_demo_project(project_id: str) -> Any:
    """
    Get demo project by ID.
    
    Args:
        project_id: Project ID
        
    Returns:
        DemoProject: Demo project data
    """
    for project in DEMO_PROJECTS:
        if project.id == project_id:
            return project
    
    # Return first project if not found
    return DEMO_PROJECTS[0]


@router.get("/projects/{project_id}/layers", response_model=List[DemoLayer])
async def get_demo_project_layers(project_id: str) -> Any:
    """
    Get demo layers for a project.
    
    Args:
        project_id: Project ID
        
    Returns:
        List[DemoLayer]: List of demo layers
    """
    return DEMO_LAYERS.get(project_id, [])


@router.get("/viewer-config")
async def get_viewer_config() -> Dict[str, Any]:
    """
    Get viewer configuration for demo.
    
    Returns:
        Dict[str, Any]: Viewer configuration
    """
    return {
        "api_url": "http://localhost:8000",
        "websocket_url": "ws://localhost:8000",
        "demo_mode": True,
        "features": {
            "2d_view": True,
            "3d_view": True,
            "edit_tools": True,
            "collaboration": True,
            "layer_management": True,
        },
        "sample_geometry": {
            "building": {
                "type": "box",
                "dimensions": [20, 30, 15],
                "position": [0, 0, 0],
                "color": "#8B4513",
            },
            "walls": [
                {
                    "type": "wall",
                    "start": [0, 0, 0],
                    "end": [20, 0, 0],
                    "height": 15,
                    "thickness": 0.3,
                    "color": "#D3D3D3",
                },
                {
                    "type": "wall", 
                    "start": [20, 0, 0],
                    "end": [20, 30, 0],
                    "height": 15,
                    "thickness": 0.3,
                    "color": "#D3D3D3",
                },
                {
                    "type": "wall",
                    "start": [20, 30, 0],
                    "end": [0, 30, 0],
                    "height": 15,
                    "thickness": 0.3,
                    "color": "#D3D3D3",
                },
                {
                    "type": "wall",
                    "start": [0, 30, 0],
                    "end": [0, 0, 0],
                    "height": 15,
                    "thickness": 0.3,
                    "color": "#D3D3D3",
                },
            ],
        },
    }