/**
 * Layer Panel component for managing project layers
 */

'use client'

import React, { useEffect, useState } from 'react'
import { Button } from '@/components/ui/button'
import { useStore } from '@/lib/store'
import { demoApi } from '@/lib/api'
import { Eye, EyeOff, Lock, Unlock, Plus, Settings } from 'lucide-react'

interface Layer {
  id: string
  name: string
  layer_type: string
  is_visible: boolean
  geometry_type: string
}

export const LayerPanel: React.FC = () => {
  const { showLayerPanel, currentProject, layers, setLayers } = useStore()
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    if (currentProject && showLayerPanel) {
      loadLayers()
    }
  }, [currentProject, showLayerPanel])

  const loadLayers = async () => {
    if (!currentProject) return
    
    setIsLoading(true)
    try {
      const response = await demoApi.getProjectLayers(currentProject.id)
      setLayers(response.data)
    } catch (error) {
      console.error('Failed to load layers:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const toggleLayerVisibility = (layerId: string) => {
    const updatedLayers = layers.map(layer =>
      layer.id === layerId 
        ? { ...layer, is_visible: !layer.is_visible }
        : layer
    )
    setLayers(updatedLayers)
  }

  const getLayerIcon = (layerType: string) => {
    const icons: Record<string, string> = {
      structure: '🏗️',
      wall: '🧱',
      opening: '🚪',
      system: '⚡',
      default: '📄',
    }
    return icons[layerType] || icons.default
  }

  if (!showLayerPanel) return null

  return (
    <div className="absolute left-4 top-4 bottom-4 w-80 bg-white rounded-lg shadow-lg flex flex-col z-10">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900">Layers</h3>
        {currentProject && (
          <p className="text-sm text-gray-600 mt-1">{currentProject.name}</p>
        )}
      </div>

      {/* Toolbar */}
      <div className="p-3 border-b border-gray-200 flex gap-2">
        <Button size="sm" variant="outline" className="flex items-center gap-1">
          <Plus className="w-4 h-4" />
          Add Layer
        </Button>
        <Button size="sm" variant="ghost" className="flex items-center gap-1">
          <Settings className="w-4 h-4" />
        </Button>
      </div>

      {/* Layer List */}
      <div className="flex-1 overflow-y-auto">
        {isLoading ? (
          <div className="p-4 text-center text-gray-500">Loading layers...</div>
        ) : layers.length === 0 ? (
          <div className="p-4 text-center text-gray-500">No layers found</div>
        ) : (
          <div className="p-2">
            {layers.map((layer, index) => (
              <div
                key={layer.id}
                className="flex items-center gap-3 p-2 rounded-md hover:bg-gray-50 group"
              >
                {/* Layer Icon */}
                <div className="text-lg">
                  {getLayerIcon(layer.layer_type)}
                </div>

                {/* Layer Info */}
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium text-gray-900 truncate">
                    {layer.name}
                  </div>
                  <div className="text-xs text-gray-500">
                    {layer.layer_type} • {layer.geometry_type}
                  </div>
                </div>

                {/* Layer Controls */}
                <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => toggleLayerVisibility(layer.id)}
                    className="w-6 h-6 p-0"
                    title={layer.is_visible ? 'Hide layer' : 'Show layer'}
                  >
                    {layer.is_visible ? (
                      <Eye className="w-3 h-3" />
                    ) : (
                      <EyeOff className="w-3 h-3 text-gray-400" />
                    )}
                  </Button>
                  
                  <Button
                    size="sm"
                    variant="ghost"
                    className="w-6 h-6 p-0"
                    title="Lock/Unlock layer"
                  >
                    <Lock className="w-3 h-3 text-gray-400" />
                  </Button>
                </div>

                {/* Z-index indicator */}
                <div className="text-xs text-gray-400 w-6 text-center">
                  {index + 1}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="p-3 border-t border-gray-200 text-xs text-gray-500">
        {layers.length} layer{layers.length !== 1 ? 's' : ''}
      </div>
    </div>
  )
}