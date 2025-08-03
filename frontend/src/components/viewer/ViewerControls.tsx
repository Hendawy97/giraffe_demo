/**
 * Viewer Controls component for Giraffe SDK viewer
 */

'use client'

import React, { useRef } from 'react'
import { Button } from '@/components/ui/button'
import { useStore } from '@/lib/store'
import { type GiraffeViewer } from '@/lib/giraffe'
import { 
  Box, 
  Layers, 
  RotateCcw, 
  ZoomIn, 
  ZoomOut, 
  Eye,
  Map,
  Box as BoxIcon,
  Move,
  Square,
  DoorOpen,
  Maximize,
} from 'lucide-react'

interface ViewerControlsProps {
  viewer?: GiraffeViewer | null
}

export const ViewerControls: React.FC<ViewerControlsProps> = ({ viewer }) => {
  const { 
    viewMode, 
    setViewMode, 
    activeTool, 
    setActiveTool,
    showLayerPanel,
    toggleLayerPanel,
    showMiniMap,
    toggleMiniMap,
  } = useStore()

  const tools = [
    { id: 'select', icon: Move, label: 'Select' },
    { id: 'wall', icon: Square, label: 'Wall' },
    { id: 'door', icon: DoorOpen, label: 'Door' },
  ] as const

  return (
    <div className="absolute top-4 right-4 z-10">
      <div className="flex flex-col gap-2 bg-white rounded-lg shadow-lg p-2">
        {/* View Mode Toggle */}
        <div className="flex gap-1">
          <Button
            variant={viewMode === '2d' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setViewMode('2d')}
            className="flex items-center gap-1"
          >
            <Map className="w-4 h-4" />
            2D
          </Button>
          <Button
            variant={viewMode === '3d' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setViewMode('3d')}
            className="flex items-center gap-1"
          >
            <BoxIcon className="w-4 h-4" />
            3D
          </Button>
        </div>

        {/* Separator */}
        <div className="border-t border-gray-200" />

        {/* Tools */}
        <div className="flex flex-col gap-1">
          <div className="text-xs text-gray-500 px-2">Tools</div>
          {tools.map((tool) => {
            const Icon = tool.icon
            return (
              <Button
                key={tool.id}
                variant={activeTool === tool.id ? 'default' : 'outline'}
                size="sm"
                onClick={() => setActiveTool(tool.id as any)}
                title={tool.label}
                className="w-8 h-8 p-0"
              >
                <Icon className="w-4 h-4" />
              </Button>
            )
          })}
        </div>

        {/* Separator */}
        <div className="border-t border-gray-200" />

        {/* View Controls */}
        <div className="flex flex-col gap-1">
          <div className="text-xs text-gray-500 px-2">View</div>
          
          <Button
            variant="outline"
            size="sm"
            onClick={() => viewer?.zoomIn()}
            title="Zoom In"
            className="w-8 h-8 p-0"
            disabled={!viewer}
          >
            <ZoomIn className="w-4 h-4" />
          </Button>

          <Button
            variant="outline"
            size="sm"
            onClick={() => viewer?.zoomOut()}
            title="Zoom Out"
            className="w-8 h-8 p-0"
            disabled={!viewer}
          >
            <ZoomOut className="w-4 h-4" />
          </Button>

          <Button
            variant="outline"
            size="sm"
            onClick={() => viewer?.resetView()}
            title="Reset View"
            className="w-8 h-8 p-0"
            disabled={!viewer}
          >
            <RotateCcw className="w-4 h-4" />
          </Button>

          <Button
            variant="outline"
            size="sm"
            onClick={() => viewer?.fitToView()}
            title="Fit to View"
            className="w-8 h-8 p-0"
            disabled={!viewer}
          >
            <Maximize className="w-4 h-4" />
          </Button>
        </div>

        {/* Separator */}
        <div className="border-t border-gray-200" />

        {/* Panel Toggles */}
        <div className="flex flex-col gap-1">
          <div className="text-xs text-gray-500 px-2">Panels</div>
          
          <Button
            variant={showLayerPanel ? "default" : "outline"}
            size="sm"
            onClick={toggleLayerPanel}
            title="Toggle Layers"
            className="w-8 h-8 p-0"
          >
            <Layers className="w-4 h-4" />
          </Button>

          <Button
            variant={showMiniMap ? "default" : "outline"}
            size="sm"
            onClick={toggleMiniMap}
            title="Toggle Mini Map"
            className="w-8 h-8 p-0"
          >
            <Eye className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </div>
  )
}