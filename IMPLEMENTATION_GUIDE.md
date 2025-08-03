# Giraffe SDK Demo App - Complete Implementation Guide

## 🏗️ Project Overview

This guide provides a complete implementation plan for building a demo application using Giraffe SDK with:
- **Backend**: FastAPI (Python)
- **Frontend**: Next.js (React/TypeScript)
- **Features**: 2D/3D Map Viewer, Navigator, Basic Editor Tools

## 📋 Table of Contents

1. [Project Architecture](#project-architecture)
2. [Planning Phase](#planning-phase)
3. [Environment Setup](#environment-setup)
4. [Backend Implementation (FastAPI)](#backend-implementation-fastapi)
5. [Frontend Implementation (Next.js)](#frontend-implementation-nextjs)
6. [Giraffe SDK Integration](#giraffe-sdk-integration)
7. [Editor Tools Implementation](#editor-tools-implementation)
8. [Testing & Deployment](#testing--deployment)

---

## 🏛️ Project Architecture

### System Architecture Diagram
```
┌─────────────────────────────────────┐
│           Frontend (Next.js)        │
│  ┌─────────────┐ ┌─────────────────┐│
│  │   Viewer    │ │  Editor Tools   ││
│  │ Component   │ │   Component     ││
│  └─────────────┘ └─────────────────┘│
│  ┌─────────────────────────────────┐ │
│  │       Giraffe JS SDK            │ │
│  └─────────────────────────────────┘ │
└─────────────────────────────────────┘
                    │ HTTP/WS
                    ▼
┌─────────────────────────────────────┐
│          Backend (FastAPI)          │
│  ┌─────────────┐ ┌─────────────────┐│
│  │ REST APIs   │ │  WebSocket      ││
│  │             │ │  Handlers       ││
│  └─────────────┘ └─────────────────┘│
│  ┌─────────────────────────────────┐ │
│  │      Database Layer             │ │
│  │   (PostgreSQL + PostGIS)        │ │
│  └─────────────────────────────────┘ │
└─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────┐
│         Giraffe Cloud               │
│      (Authentication & Assets)      │
└─────────────────────────────────────┘
```

### Tech Stack
- **Frontend**: Next.js 14, React 18, TypeScript, Tailwind CSS
- **Backend**: FastAPI, SQLAlchemy, PostgreSQL, PostGIS
- **SDK**: Giraffe JavaScript SDK
- **Real-time**: WebSockets
- **Authentication**: JWT
- **Deployment**: Docker, Docker Compose

---

## 📝 Planning Phase

### Phase 1: Foundation (Week 1)
- [ ] Repository setup and structure
- [ ] Docker environment configuration
- [ ] Database schema design
- [ ] Authentication system
- [ ] Basic API endpoints

### Phase 2: Core Viewer (Week 2)
- [ ] Giraffe SDK integration
- [ ] 2D/3D viewer implementation
- [ ] Map navigation controls
- [ ] Project loading functionality

### Phase 3: Editor Tools (Week 3)
- [ ] Basic drawing tools
- [ ] Selection and manipulation
- [ ] Real-time collaboration
- [ ] Save/load functionality

### Phase 4: Polish & Deploy (Week 4)
- [ ] UI/UX improvements
- [ ] Error handling
- [ ] Performance optimization
- [ ] Production deployment

### Features Breakdown

#### Core Features
1. **Map Viewer**
   - 2D/3D toggle
   - Pan, zoom, rotate
   - Layer management
   - Mini-map

2. **Navigation**
   - Scene navigation
   - Bookmarks/viewpoints
   - Search functionality

3. **Basic Editor Tools**
   - Select tool
   - Draw walls/lines
   - Move/transform objects
   - Delete objects

4. **Real-time Collaboration**
   - Live cursor tracking
   - Edit synchronization
   - User presence

---

## 🔧 Environment Setup

### Prerequisites
- Node.js 18+
- Python 3.11+
- Docker & Docker Compose
- Git
- Giraffe SDK access credentials

### 1. Repository Structure Setup

```bash
# Navigate to your cloned repo
cd giraffe_demo

# Create the project structure
mkdir -p {apps/{api,web},packages/{shared-types,ui-components},infra}

# Initialize the monorepo
echo '{"name": "giraffe-demo", "private": true, "workspaces": ["apps/*", "packages/*"]}' > package.json
```

### 2. Docker Environment

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  postgres:
    image: postgis/postgis:15-3.3
    environment:
      POSTGRES_DB: giraffe_demo
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  api:
    build:
      context: ./apps/api
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://postgres:password@postgres:5432/giraffe_demo
      REDIS_URL: redis://redis:6379
    depends_on:
      - postgres
      - redis
    volumes:
      - ./apps/api:/app

  web:
    build:
      context: ./apps/web
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000
    depends_on:
      - api
    volumes:
      - ./apps/web:/app

volumes:
  postgres_data:
```

---

## 🐍 Backend Implementation (FastAPI)

### 1. FastAPI Project Setup

```bash
cd apps/api

# Initialize Python project
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Create requirements.txt
cat > requirements.txt << EOF
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
alembic==1.12.1
psycopg2-binary==2.9.9
geoalchemy2==0.14.2
pydantic==2.5.0
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
python-multipart==0.0.6
websockets==12.0
redis==5.0.1
python-dotenv==1.0.0
EOF

pip install -r requirements.txt
```

### 2. Project Structure

```bash
mkdir -p {app/{api,core,db,models,schemas,services},alembic/versions}

# Create the main application structure
apps/api/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── security.py
│   │   └── database.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── auth.py
│   │       ├── projects.py
│   │       └── websocket.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── project.py
│   │   └── geometry.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── project.py
│   │   └── geometry.py
│   └── services/
│       ├── __init__.py
│       ├── auth.py
│       └── giraffe.py
├── alembic/
├── alembic.ini
├── requirements.txt
└── Dockerfile
```

### 3. Core Configuration

Create `app/core/config.py`:

```python
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/giraffe_demo"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    
    # Giraffe SDK
    GIRAFFE_API_URL: str = "https://api.giraffe.com"
    GIRAFFE_CLIENT_ID: Optional[str] = None
    GIRAFFE_CLIENT_SECRET: Optional[str] = None
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000"]
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### 4. Database Models

Create `app/models/project.py`:

```python
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from geoalchemy2 import Geometry
import uuid

from app.core.database import Base

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    # Giraffe-specific fields
    giraffe_project_id = Column(String)
    giraffe_model_url = Column(String)

class Layer(Base):
    __tablename__ = "layers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), nullable=False)
    name = Column(String, nullable=False)
    layer_type = Column(String)  # 'wall', 'floor', 'roof', etc.
    geometry = Column(Geometry('GEOMETRY'))
    properties = Column(Text)  # JSON string
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class EditHistory(Base):
    __tablename__ = "edit_history"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), nullable=False)
    user_id = Column(String)  # From JWT
    action = Column(String)  # 'create', 'update', 'delete'
    object_type = Column(String)
    object_id = Column(UUID(as_uuid=True))
    changes = Column(Text)  # JSON string
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
```

### 5. Main FastAPI Application

Create `app/main.py`:

```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import json

from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1 import auth, projects, websocket

# Create tables
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting up...")
    yield
    # Shutdown
    print("Shutting down...")

app = FastAPI(
    title="Giraffe Demo API",
    description="FastAPI backend for Giraffe SDK demo",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(projects.router, prefix="/api/v1/projects", tags=["projects"])
app.include_router(websocket.router, prefix="/api/v1/ws", tags=["websocket"])

@app.get("/")
async def root():
    return {"message": "Giraffe Demo API"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
```

### 6. API Endpoints

Create `app/api/v1/projects.py`:

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.core.database import get_db
from app.models.project import Project, Layer
from app.schemas.project import ProjectCreate, ProjectResponse, LayerCreate, LayerResponse

router = APIRouter()

@router.post("/", response_model=ProjectResponse)
async def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db)
):
    db_project = Project(
        name=project.name,
        description=project.description,
        giraffe_project_id=project.giraffe_project_id
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@router.get("/", response_model=List[ProjectResponse])
async def get_projects(db: Session = Depends(get_db)):
    return db.query(Project).filter(Project.is_active == True).all()

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: uuid.UUID, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.get("/{project_id}/layers", response_model=List[LayerResponse])
async def get_project_layers(project_id: uuid.UUID, db: Session = Depends(get_db)):
    return db.query(Layer).filter(Layer.project_id == project_id).all()

@router.post("/{project_id}/layers", response_model=LayerResponse)
async def create_layer(
    project_id: uuid.UUID,
    layer: LayerCreate,
    db: Session = Depends(get_db)
):
    db_layer = Layer(
        project_id=project_id,
        name=layer.name,
        layer_type=layer.layer_type,
        geometry=layer.geometry,
        properties=layer.properties
    )
    db.add(db_layer)
    db.commit()
    db.refresh(db_layer)
    return db_layer
```

### 7. WebSocket Handler

Create `app/api/v1/websocket.py`:

```python
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List
import json
import uuid

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, project_id: str):
        await websocket.accept()
        if project_id not in self.active_connections:
            self.active_connections[project_id] = []
        self.active_connections[project_id].append(websocket)
    
    def disconnect(self, websocket: WebSocket, project_id: str):
        if project_id in self.active_connections:
            self.active_connections[project_id].remove(websocket)
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    
    async def broadcast_to_project(self, message: str, project_id: str):
        if project_id in self.active_connections:
            for connection in self.active_connections[project_id]:
                await connection.send_text(message)

manager = ConnectionManager()

@router.websocket("/projects/{project_id}")
async def websocket_endpoint(websocket: WebSocket, project_id: str):
    await manager.connect(websocket, project_id)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Handle different message types
            if message_data.get("type") == "edit":
                # Broadcast edit to all project participants
                await manager.broadcast_to_project(data, project_id)
            elif message_data.get("type") == "cursor":
                # Broadcast cursor position
                await manager.broadcast_to_project(data, project_id)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, project_id)
```

---

## ⚛️ Frontend Implementation (Next.js)

### 1. Next.js Project Setup

```bash
cd apps/web

# Create Next.js project
npx create-next-app@latest . --typescript --tailwind --eslint --app --src-dir

# Install additional dependencies
npm install @tanstack/react-query zustand axios socket.io-client lucide-react

# Install Giraffe SDK (replace with actual package name)
npm install @giraffe/sdk
```

### 2. Project Structure

```
apps/web/
├── src/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   ├── viewer/
│   │   │   └── page.tsx
│   │   └── editor/
│   │       └── page.tsx
│   ├── components/
│   │   ├── ui/
│   │   ├── viewer/
│   │   │   ├── GiraffeViewer.tsx
│   │   │   ├── NavigationControls.tsx
│   │   │   └── LayerPanel.tsx
│   │   ├── editor/
│   │   │   ├── EditorToolbar.tsx
│   │   │   ├── PropertyPanel.tsx
│   │   │   └── tools/
│   │   └── layout/
│   │       ├── Header.tsx
│   │       └── Sidebar.tsx
│   ├── hooks/
│   │   ├── useGiraffe.ts
│   │   ├── useProjects.ts
│   │   └── useWebSocket.ts
│   ├── stores/
│   │   ├── viewerStore.ts
│   │   ├── editorStore.ts
│   │   └── authStore.ts
│   ├── lib/
│   │   ├── api.ts
│   │   ├── giraffe.ts
│   │   └── utils.ts
│   └── types/
│       ├── giraffe.ts
│       ├── project.ts
│       └── api.ts
├── public/
└── package.json
```

### 3. Store Configuration (Zustand)

Create `src/stores/viewerStore.ts`:

```typescript
import { create } from 'zustand'

interface ViewerState {
  // Viewer state
  viewMode: '2d' | '3d'
  isLoading: boolean
  currentProject: string | null
  
  // Navigation
  camera: {
    position: [number, number, number]
    target: [number, number, number]
  }
  
  // UI state
  showMiniMap: boolean
  showLayerPanel: boolean
  
  // Actions
  setViewMode: (mode: '2d' | '3d') => void
  setLoading: (loading: boolean) => void
  setCurrentProject: (projectId: string | null) => void
  updateCamera: (camera: { position: [number, number, number]; target: [number, number, number] }) => void
  toggleMiniMap: () => void
  toggleLayerPanel: () => void
}

export const useViewerStore = create<ViewerState>((set) => ({
  viewMode: '3d',
  isLoading: false,
  currentProject: null,
  camera: {
    position: [0, 0, 10],
    target: [0, 0, 0]
  },
  showMiniMap: true,
  showLayerPanel: true,
  
  setViewMode: (mode) => set({ viewMode: mode }),
  setLoading: (loading) => set({ isLoading: loading }),
  setCurrentProject: (projectId) => set({ currentProject: projectId }),
  updateCamera: (camera) => set({ camera }),
  toggleMiniMap: () => set((state) => ({ showMiniMap: !state.showMiniMap })),
  toggleLayerPanel: () => set((state) => ({ showLayerPanel: !state.showLayerPanel })),
}))
```

### 4. Giraffe SDK Hook

Create `src/hooks/useGiraffe.ts`:

```typescript
import { useEffect, useRef, useState } from 'react'
import { useViewerStore } from '@/stores/viewerStore'

// Import Giraffe SDK (adjust import based on actual SDK)
// import { Viewer } from '@giraffe/sdk'

interface UseGiraffeProps {
  containerId: string
  projectId?: string
}

export function useGiraffe({ containerId, projectId }: UseGiraffeProps) {
  const viewerRef = useRef<any>(null)
  const [isInitialized, setIsInitialized] = useState(false)
  const { viewMode, setLoading } = useViewerStore()

  useEffect(() => {
    if (typeof window === 'undefined') return

    const initializeViewer = async () => {
      try {
        setLoading(true)
        
        // Initialize Giraffe viewer
        // Replace with actual Giraffe SDK initialization
        const viewer = new (window as any).Giraffe.Viewer({
          container: containerId,
          mode: viewMode,
          // Add authentication token
          token: 'your-giraffe-token',
          // Additional configuration
          enableControls: true,
          enableMiniMap: true,
        })

        viewerRef.current = viewer
        setIsInitialized(true)
        
        // Set up event listeners
        viewer.on('cameraChange', (camera: any) => {
          useViewerStore.getState().updateCamera(camera)
        })

        viewer.on('objectSelect', (object: any) => {
          console.log('Object selected:', object)
        })

        // Load project if provided
        if (projectId) {
          await viewer.loadProject(projectId)
        }

      } catch (error) {
        console.error('Failed to initialize Giraffe viewer:', error)
      } finally {
        setLoading(false)
      }
    }

    initializeViewer()

    return () => {
      if (viewerRef.current) {
        viewerRef.current.destroy()
      }
    }
  }, [containerId, projectId])

  // Update view mode
  useEffect(() => {
    if (viewerRef.current && isInitialized) {
      viewerRef.current.setMode(viewMode)
    }
  }, [viewMode, isInitialized])

  return {
    viewer: viewerRef.current,
    isInitialized
  }
}
```

### 5. Main Viewer Component

Create `src/components/viewer/GiraffeViewer.tsx`:

```typescript
'use client'

import { useEffect, useRef } from 'react'
import { useGiraffe } from '@/hooks/useGiraffe'
import { useViewerStore } from '@/stores/viewerStore'
import NavigationControls from './NavigationControls'
import LayerPanel from './LayerPanel'

interface GiraffeViewerProps {
  projectId?: string
  enableEditor?: boolean
}

export default function GiraffeViewer({ projectId, enableEditor = false }: GiraffeViewerProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const { isLoading, showLayerPanel } = useViewerStore()
  
  const { viewer, isInitialized } = useGiraffe({
    containerId: 'giraffe-viewer-container',
    projectId
  })

  return (
    <div className="relative w-full h-full">
      {/* Loading overlay */}
      {isLoading && (
        <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="text-white text-lg">Loading...</div>
        </div>
      )}

      {/* Viewer container */}
      <div 
        id="giraffe-viewer-container"
        ref={containerRef}
        className="w-full h-full"
      />

      {/* Navigation controls */}
      {isInitialized && (
        <NavigationControls 
          viewer={viewer}
          enableEditor={enableEditor}
        />
      )}

      {/* Layer panel */}
      {showLayerPanel && isInitialized && (
        <LayerPanel 
          viewer={viewer}
          projectId={projectId}
        />
      )}
    </div>
  )
}
```

### 6. Navigation Controls

Create `src/components/viewer/NavigationControls.tsx`:

```typescript
'use client'

import { Button } from '@/components/ui/button'
import { useViewerStore } from '@/stores/viewerStore'
import { 
  View, 
  Box, 
  Map, 
  Layers,
  RotateCcw,
  ZoomIn,
  ZoomOut
} from 'lucide-react'

interface NavigationControlsProps {
  viewer: any
  enableEditor?: boolean
}

export default function NavigationControls({ viewer, enableEditor }: NavigationControlsProps) {
  const { 
    viewMode, 
    setViewMode, 
    showMiniMap, 
    toggleMiniMap,
    showLayerPanel,
    toggleLayerPanel
  } = useViewerStore()

  const handleViewModeToggle = () => {
    const newMode = viewMode === '2d' ? '3d' : '2d'
    setViewMode(newMode)
  }

  const handleZoomIn = () => {
    viewer?.zoomIn()
  }

  const handleZoomOut = () => {
    viewer?.zoomOut()
  }

  const handleResetView = () => {
    viewer?.resetView()
  }

  return (
    <div className="absolute top-4 right-4 z-10">
      <div className="flex flex-col gap-2 bg-white rounded-lg shadow-lg p-2">
        {/* View mode toggle */}
        <Button
          variant="outline"
          size="sm"
          onClick={handleViewModeToggle}
          title={`Switch to ${viewMode === '2d' ? '3D' : '2D'} view`}
        >
          {viewMode === '2d' ? <Box className="w-4 h-4" /> : <View className="w-4 h-4" />}
        </Button>

        {/* Zoom controls */}
        <Button
          variant="outline"
          size="sm"
          onClick={handleZoomIn}
          title="Zoom In"
        >
          <ZoomIn className="w-4 h-4" />
        </Button>

        <Button
          variant="outline"
          size="sm"
          onClick={handleZoomOut}
          title="Zoom Out"
        >
          <ZoomOut className="w-4 h-4" />
        </Button>

        {/* Reset view */}
        <Button
          variant="outline"
          size="sm"
          onClick={handleResetView}
          title="Reset View"
        >
          <RotateCcw className="w-4 h-4" />
        </Button>

        {/* Toggle mini map */}
        <Button
          variant={showMiniMap ? "default" : "outline"}
          size="sm"
          onClick={toggleMiniMap}
          title="Toggle Mini Map"
        >
          <Map className="w-4 h-4" />
        </Button>

        {/* Toggle layers panel */}
        <Button
          variant={showLayerPanel ? "default" : "outline"}
          size="sm"
          onClick={toggleLayerPanel}
          title="Toggle Layers"
        >
          <Layers className="w-4 h-4" />
        </Button>
      </div>
    </div>
  )
}
```

---

## 🔧 Editor Tools Implementation

### 1. Editor Store

Create `src/stores/editorStore.ts`:

```typescript
import { create } from 'zustand'

export type EditorTool = 'select' | 'wall' | 'door' | 'window' | 'move' | 'delete'

interface EditorState {
  // Current tool
  activeTool: EditorTool
  
  // Selection
  selectedObjects: string[]
  
  // Drawing state
  isDrawing: boolean
  drawingPoints: [number, number][]
  
  // Clipboard
  clipboardObjects: any[]
  
  // History
  canUndo: boolean
  canRedo: boolean
  
  // Actions
  setActiveTool: (tool: EditorTool) => void
  selectObject: (objectId: string) => void
  selectMultiple: (objectIds: string[]) => void
  clearSelection: () => void
  startDrawing: (point: [number, number]) => void
  addDrawingPoint: (point: [number, number]) => void
  finishDrawing: () => void
  cancelDrawing: () => void
  copySelection: () => void
  paste: () => void
  undo: () => void
  redo: () => void
}

export const useEditorStore = create<EditorState>((set, get) => ({
  activeTool: 'select',
  selectedObjects: [],
  isDrawing: false,
  drawingPoints: [],
  clipboardObjects: [],
  canUndo: false,
  canRedo: false,
  
  setActiveTool: (tool) => set({ activeTool: tool }),
  
  selectObject: (objectId) => set({ selectedObjects: [objectId] }),
  
  selectMultiple: (objectIds) => set({ selectedObjects: objectIds }),
  
  clearSelection: () => set({ selectedObjects: [] }),
  
  startDrawing: (point) => set({ 
    isDrawing: true, 
    drawingPoints: [point] 
  }),
  
  addDrawingPoint: (point) => set((state) => ({
    drawingPoints: [...state.drawingPoints, point]
  })),
  
  finishDrawing: () => set({ 
    isDrawing: false, 
    drawingPoints: [] 
  }),
  
  cancelDrawing: () => set({ 
    isDrawing: false, 
    drawingPoints: [] 
  }),
  
  copySelection: () => {
    // Implementation for copying selected objects
    console.log('Copy selection')
  },
  
  paste: () => {
    // Implementation for pasting objects
    console.log('Paste objects')
  },
  
  undo: () => {
    // Implementation for undo
    console.log('Undo')
  },
  
  redo: () => {
    // Implementation for redo
    console.log('Redo')
  },
}))
```

### 2. Editor Toolbar

Create `src/components/editor/EditorToolbar.tsx`:

```typescript
'use client'

import { Button } from '@/components/ui/button'
import { useEditorStore, EditorTool } from '@/stores/editorStore'
import { 
  MousePointer2, 
  Square, 
  DoorOpen, 
  RectangleHorizontal,
  Move,
  Trash2,
  Copy,
  Clipboard,
  Undo,
  Redo,
  Save
} from 'lucide-react'

const toolIcons: Record<EditorTool, any> = {
  select: MousePointer2,
  wall: Square,
  door: DoorOpen,
  window: RectangleHorizontal,
  move: Move,
  delete: Trash2,
}

export default function EditorToolbar() {
  const { 
    activeTool, 
    setActiveTool,
    selectedObjects,
    canUndo,
    canRedo,
    copySelection,
    paste,
    undo,
    redo
  } = useEditorStore()

  const tools: { id: EditorTool; label: string; icon: any }[] = [
    { id: 'select', label: 'Select', icon: MousePointer2 },
    { id: 'wall', label: 'Wall', icon: Square },
    { id: 'door', label: 'Door', icon: DoorOpen },
    { id: 'window', label: 'Window', icon: RectangleHorizontal },
    { id: 'move', label: 'Move', icon: Move },
    { id: 'delete', label: 'Delete', icon: Trash2 },
  ]

  return (
    <div className="absolute top-4 left-4 z-10">
      <div className="flex flex-col gap-2 bg-white rounded-lg shadow-lg p-2">
        {/* Drawing tools */}
        <div className="flex flex-col gap-1">
          <div className="text-xs text-gray-500 px-2">Tools</div>
          {tools.map((tool) => {
            const Icon = tool.icon
            return (
              <Button
                key={tool.id}
                variant={activeTool === tool.id ? "default" : "outline"}
                size="sm"
                onClick={() => setActiveTool(tool.id)}
                title={tool.label}
                className="w-10 h-10"
              >
                <Icon className="w-4 h-4" />
              </Button>
            )
          })}
        </div>

        {/* Separator */}
        <div className="border-t border-gray-200" />

        {/* Edit actions */}
        <div className="flex flex-col gap-1">
          <div className="text-xs text-gray-500 px-2">Edit</div>
          
          <Button
            variant="outline"
            size="sm"
            onClick={copySelection}
            disabled={selectedObjects.length === 0}
            title="Copy"
            className="w-10 h-10"
          >
            <Copy className="w-4 h-4" />
          </Button>

          <Button
            variant="outline"
            size="sm"
            onClick={paste}
            title="Paste"
            className="w-10 h-10"
          >
            <Clipboard className="w-4 h-4" />
          </Button>

          <Button
            variant="outline"
            size="sm"
            onClick={undo}
            disabled={!canUndo}
            title="Undo"
            className="w-10 h-10"
          >
            <Undo className="w-4 h-4" />
          </Button>

          <Button
            variant="outline"
            size="sm"
            onClick={redo}
            disabled={!canRedo}
            title="Redo"
            className="w-10 h-10"
          >
            <Redo className="w-4 h-4" />
          </Button>
        </div>

        {/* Separator */}
        <div className="border-t border-gray-200" />

        {/* Save */}
        <Button
          variant="outline"
          size="sm"
          onClick={() => console.log('Save project')}
          title="Save"
          className="w-10 h-10"
        >
          <Save className="w-4 h-4" />
        </Button>
      </div>
    </div>
  )
}
```

### 3. WebSocket Integration

Create `src/hooks/useWebSocket.ts`:

```typescript
import { useEffect, useRef, useState } from 'react'
import { io, Socket } from 'socket.io-client'

interface UseWebSocketProps {
  projectId: string
  onMessage?: (data: any) => void
}

export function useWebSocket({ projectId, onMessage }: UseWebSocketProps) {
  const socketRef = useRef<WebSocket | null>(null)
  const [isConnected, setIsConnected] = useState(false)

  useEffect(() => {
    if (!projectId) return

    // Create WebSocket connection
    const wsUrl = `ws://localhost:8000/api/v1/ws/projects/${projectId}`
    const socket = new WebSocket(wsUrl)

    socket.onopen = () => {
      console.log('WebSocket connected')
      setIsConnected(true)
    }

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        onMessage?.(data)
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error)
      }
    }

    socket.onclose = () => {
      console.log('WebSocket disconnected')
      setIsConnected(false)
    }

    socket.onerror = (error) => {
      console.error('WebSocket error:', error)
    }

    socketRef.current = socket

    return () => {
      socket.close()
    }
  }, [projectId, onMessage])

  const sendMessage = (data: any) => {
    if (socketRef.current && isConnected) {
      socketRef.current.send(JSON.stringify(data))
    }
  }

  return {
    isConnected,
    sendMessage
  }
}
```

---

## 🧪 Testing & Deployment

### 1. Development Scripts

Add to `package.json` in root:

```json
{
  "scripts": {
    "dev": "docker-compose up -d && npm run dev:web",
    "dev:api": "cd apps/api && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000",
    "dev:web": "cd apps/web && npm run dev",
    "build": "npm run build:api && npm run build:web",
    "build:api": "cd apps/api && docker build -t giraffe-demo-api .",
    "build:web": "cd apps/web && npm run build",
    "test": "npm run test:api && npm run test:web",
    "test:api": "cd apps/api && pytest",
    "test:web": "cd apps/web && npm run test"
  }
}
```

### 2. Environment Variables

Create `.env.example`:

```bash
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/giraffe_demo

# Redis
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Giraffe SDK
GIRAFFE_API_URL=https://api.giraffe.com
GIRAFFE_CLIENT_ID=your-giraffe-client-id
GIRAFFE_CLIENT_SECRET=your-giraffe-client-secret

# Next.js
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

### 3. Production Deployment

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - api
      - web

  api:
    build:
      context: ./apps/api
      dockerfile: Dockerfile.prod
    environment:
      DATABASE_URL: ${DATABASE_URL}
      REDIS_URL: ${REDIS_URL}
      SECRET_KEY: ${SECRET_KEY}
    depends_on:
      - postgres
      - redis

  web:
    build:
      context: ./apps/web
      dockerfile: Dockerfile.prod
    environment:
      NEXT_PUBLIC_API_URL: ${NEXT_PUBLIC_API_URL}

  postgres:
    image: postgis/postgis:15-3.3
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine

volumes:
  postgres_data:
```

---

## 📋 Implementation Checklist

### Phase 1: Foundation ✅
- [ ] Repository setup and structure
- [ ] Docker environment configuration
- [ ] Database schema and models
- [ ] FastAPI basic setup with health endpoints
- [ ] Next.js project initialization
- [ ] Basic authentication system

### Phase 2: Core Viewer ✅
- [ ] Giraffe SDK integration
- [ ] Basic viewer component
- [ ] 2D/3D toggle functionality
- [ ] Navigation controls
- [ ] Project loading from API
- [ ] WebSocket connection setup

### Phase 3: Editor Tools ✅
- [ ] Editor toolbar component
- [ ] Basic tools (select, wall, door, window)
- [ ] Drawing interaction handlers
- [ ] Object selection and manipulation
- [ ] Real-time collaboration via WebSocket
- [ ] Save/load functionality

### Phase 4: Polish & Deploy
- [ ] Error handling and loading states
- [ ] Performance optimization
- [ ] Unit and integration tests
- [ ] Production Docker setup
- [ ] CI/CD pipeline
- [ ] Documentation completion

---

## 🚀 Getting Started

1. **Clone and setup the repository:**
   ```bash
   git clone <repository-url>
   cd giraffe_demo
   cp .env.example .env
   # Edit .env with your actual values
   ```

2. **Start the development environment:**
   ```bash
   docker-compose up -d postgres redis
   ```

3. **Run the backend:**
   ```bash
   cd apps/api
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

4. **Run the frontend:**
   ```bash
   cd apps/web
   npm install
   npm run dev
   ```

5. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

---

## 📚 Additional Resources

- [Giraffe SDK Documentation](https://docs.giraffe.com)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Next.js Documentation](https://nextjs.org/docs)
- [Zustand State Management](https://github.com/pmndrs/zustand)
- [TanStack Query](https://tanstack.com/query)