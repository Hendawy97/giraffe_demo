/**
 * Zustand store for application state management
 */

import { create } from 'zustand'

export type ViewMode = '2d' | '3d'
export type EditorTool = 'select' | 'wall' | 'door' | 'window' | 'move' | 'delete'

interface Project {
  id: string
  name: string
  description: string
  created_at: string
  layers_count: number
  is_public: boolean
}

interface Layer {
  id: string
  name: string
  layer_type: string
  is_visible: boolean
  geometry_type: string
}

interface ViewerState {
  // View settings
  viewMode: ViewMode
  isLoading: boolean
  
  // Project data
  currentProject: Project | null
  projects: Project[]
  layers: Layer[]
  
  // Editor state
  activeTool: EditorTool
  selectedObjects: string[]
  
  // UI state
  showLayerPanel: boolean
  showToolbar: boolean
  showMiniMap: boolean
  
  // Actions
  setViewMode: (mode: ViewMode) => void
  setLoading: (loading: boolean) => void
  setCurrentProject: (project: Project | null) => void
  setProjects: (projects: Project[]) => void
  setLayers: (layers: Layer[]) => void
  setActiveTool: (tool: EditorTool) => void
  toggleLayerPanel: () => void
  toggleToolbar: () => void
  toggleMiniMap: () => void
  selectObject: (objectId: string) => void
  clearSelection: () => void
}

export const useStore = create<ViewerState>((set) => ({
  // Initial state
  viewMode: '3d',
  isLoading: false,
  currentProject: null,
  projects: [],
  layers: [],
  activeTool: 'select',
  selectedObjects: [],
  showLayerPanel: true,
  showToolbar: true,
  showMiniMap: true,
  
  // Actions
  setViewMode: (mode) => set({ viewMode: mode }),
  setLoading: (loading) => set({ isLoading: loading }),
  setCurrentProject: (project) => set({ currentProject: project }),
  setProjects: (projects) => set({ projects }),
  setLayers: (layers) => set({ layers }),
  setActiveTool: (tool) => set({ activeTool: tool }),
  toggleLayerPanel: () => set((state) => ({ showLayerPanel: !state.showLayerPanel })),
  toggleToolbar: () => set((state) => ({ showToolbar: !state.showToolbar })),
  toggleMiniMap: () => set((state) => ({ showMiniMap: !state.showMiniMap })),
  selectObject: (objectId) => set((state) => ({ 
    selectedObjects: [...state.selectedObjects, objectId] 
  })),
  clearSelection: () => set({ selectedObjects: [] }),
}))