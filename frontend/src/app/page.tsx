/**
 * Main Giraffe Demo Application Page
 */

'use client'

import React, { useEffect, useState, useRef } from 'react'
import { GiraffeViewerComponent } from '@/components/viewer/GiraffeViewer'
import { ViewerControls } from '@/components/viewer/ViewerControls'
import { LayerPanel } from '@/components/layout/LayerPanel'
import { useStore } from '@/lib/store'
import { demoApi } from '@/lib/api'
import { type GiraffeViewer } from '@/lib/giraffe'

export default function HomePage() {
  const { 
    setProjects, 
    setCurrentProject, 
    currentProject,
    projects,
    isLoading 
  } = useStore()
  
  const [viewerInstance, setViewerInstance] = useState<GiraffeViewer | null>(null)

  // Load demo projects on mount
  useEffect(() => {
    loadProjects()
  }, [])

  const loadProjects = async () => {
    try {
      const response = await demoApi.getProjects()
      setProjects(response.data)
      
      // Set first project as current
      if (response.data.length > 0) {
        setCurrentProject(response.data[0])
      }
    } catch (error) {
      console.error('Failed to load projects:', error)
    }
  }

  return (
    <div className="h-screen w-screen bg-gray-100 flex flex-col overflow-hidden">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <h1 className="text-2xl font-bold text-gray-900">
            🦒 Giraffe SDK Demo
          </h1>
          
          {/* Project Selector */}
          {projects.length > 0 && (
            <select 
              value={currentProject?.id || ''}
              onChange={(e) => {
                const project = projects.find(p => p.id === e.target.value)
                if (project) setCurrentProject(project)
              }}
              className="px-3 py-2 border border-gray-300 rounded-md bg-white text-sm"
            >
              {projects.map(project => (
                <option key={project.id} value={project.id}>
                  {project.name}
                </option>
              ))}
            </select>
          )}
        </div>

        <div className="flex items-center gap-4">
          {/* Status Indicator */}
          <div className="flex items-center gap-2 text-sm">
            <div className={`w-2 h-2 rounded-full ${isLoading ? 'bg-yellow-500' : 'bg-green-500'}`} />
            <span className="text-gray-600">
              {isLoading ? 'Loading...' : 'Ready'}
            </span>
          </div>

          {/* Project Info */}
          {currentProject && (
            <div className="text-sm text-gray-600">
              {currentProject.layers_count} layers • {currentProject.is_public ? 'Public' : 'Private'}
            </div>
          )}
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 relative overflow-hidden">
        {/* Giraffe Viewer */}
        <GiraffeViewerComponent 
          projectId={currentProject?.id}
          className="absolute inset-0"
        />

        {/* Viewer Controls */}
        <ViewerControls viewer={viewerInstance} />

        {/* Layer Panel */}
        <LayerPanel />

        {/* Demo Information Panel */}
        <div className="absolute bottom-4 right-4 bg-white rounded-lg shadow-lg p-4 max-w-sm">
          <h3 className="font-semibold text-gray-900 mb-2">🦒 Giraffe SDK Demo</h3>
          <ul className="text-sm text-gray-600 space-y-1">
            <li>✅ 2D/3D View Toggle</li>
            <li>✅ Interactive Navigation</li>
            <li>✅ Layer Management</li>
            <li>✅ Basic Editor Tools</li>
            <li>✅ Real-time Updates</li>
          </ul>
          
          <div className="mt-3 pt-3 border-t border-gray-200 text-xs text-gray-500">
            <p>Demo using Giraffe SDK integration patterns</p>
            <p className="mt-1">
              API: <span className="font-mono text-green-600">localhost:8000</span>
            </p>
            <p>
              Frontend: <span className="font-mono text-blue-600">localhost:3000</span>
            </p>
          </div>
        </div>

        {/* Loading Overlay */}
        {isLoading && (
          <div className="absolute inset-0 bg-black bg-opacity-10 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-lg p-6 flex items-center gap-3">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
              <span className="text-gray-700">Loading Giraffe SDK...</span>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}