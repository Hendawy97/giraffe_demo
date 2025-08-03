/**
 * Giraffe SDK Viewer Component
 */

'use client'

import React, { useEffect, useRef, useState } from 'react'
import { useStore } from '@/lib/store'
import { initializeGiraffe, type GiraffeViewer } from '@/lib/giraffe'

interface GiraffeViewerProps {
  projectId?: string
  className?: string
}

export const GiraffeViewerComponent: React.FC<GiraffeViewerProps> = ({ 
  projectId, 
  className = '' 
}) => {
  const containerRef = useRef<HTMLDivElement>(null)
  const viewerRef = useRef<GiraffeViewer | null>(null)
  const [isInitialized, setIsInitialized] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  const { 
    viewMode, 
    setLoading, 
    activeTool,
    currentProject 
  } = useStore()

  // Initialize Giraffe SDK
  useEffect(() => {
    let mounted = true

    const initViewer = async () => {
      try {
        setLoading(true)
        setError(null)
        
        // Initialize Giraffe SDK
        await initializeGiraffe()
        
        if (!mounted || !containerRef.current) return

        // Create viewer instance
        const viewer = new window.Giraffe!.Viewer({
          container: containerRef.current,
          mode: viewMode,
          enableControls: true,
          enableMiniMap: true,
          theme: 'light',
        })

        viewerRef.current = viewer
        
        // Set up event listeners
        viewer.on('projectLoaded', (data: any) => {
          console.log('Project loaded:', data)
        })

        viewer.on('modeChanged', (data: any) => {
          console.log('Mode changed:', data)
        })

        viewer.on('objectSelected', (data: any) => {
          console.log('Object selected:', data)
        })

        viewer.on('toolChanged', (data: any) => {
          console.log('Tool changed:', data)
        })

        viewer.on('objectAdded', (data: any) => {
          console.log('Object added:', data)
        })

        viewer.on('error', (error: any) => {
          console.error('Giraffe viewer error:', error)
          setError(error.message || 'Viewer error occurred')
        })

        setIsInitialized(true)
        
        // Load project if provided
        if (projectId) {
          await viewer.loadProject(projectId)
        }

      } catch (err) {
        console.error('Failed to initialize Giraffe viewer:', err)
        setError(err instanceof Error ? err.message : 'Failed to initialize viewer')
      } finally {
        setLoading(false)
      }
    }

    initViewer()

    return () => {
      mounted = false
      if (viewerRef.current) {
        viewerRef.current.destroy()
        viewerRef.current = null
      }
    }
  }, [projectId])

  // Update view mode when changed
  useEffect(() => {
    if (viewerRef.current && isInitialized) {
      viewerRef.current.setMode(viewMode)
    }
  }, [viewMode, isInitialized])

  // Update active tool when changed
  useEffect(() => {
    if (viewerRef.current && isInitialized) {
      viewerRef.current.setTool(activeTool)
    }
  }, [activeTool, isInitialized])

  // Load different project
  useEffect(() => {
    if (viewerRef.current && isInitialized && currentProject) {
      viewerRef.current.loadProject(currentProject.id)
    }
  }, [currentProject, isInitialized])

  return (
    <div className={`relative w-full h-full ${className}`}>
      {/* Viewer Container */}
      <div 
        ref={containerRef} 
        className="w-full h-full"
        style={{ minHeight: '400px' }}
      />
      
      {/* Loading Overlay */}
      {!isInitialized && !error && (
        <div className="absolute inset-0 bg-gray-100 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Initializing Giraffe SDK...</p>
          </div>
        </div>
      )}
      
      {/* Error State */}
      {error && (
        <div className="absolute inset-0 bg-red-50 flex items-center justify-center">
          <div className="text-center p-6">
            <div className="text-red-600 text-xl mb-2">⚠️</div>
            <h3 className="text-lg font-semibold text-red-800 mb-2">Viewer Error</h3>
            <p className="text-red-600 mb-4">{error}</p>
            <button 
              onClick={() => window.location.reload()}
              className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
            >
              Reload Page
            </button>
          </div>
        </div>
      )}
      
      {/* SDK Info Overlay */}
      {isInitialized && (
        <div className="absolute bottom-4 left-4 bg-black bg-opacity-50 text-white px-3 py-1 rounded text-sm">
          Giraffe SDK v{window.Giraffe?.version} - {viewMode.toUpperCase()} Mode
        </div>
      )}
    </div>
  )
}