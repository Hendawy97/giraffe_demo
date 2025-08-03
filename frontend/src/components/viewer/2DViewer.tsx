/**
 * 2D Viewer component for top-down view
 */

'use client'

import React, { useRef, useEffect, useState } from 'react'

interface Point {
  x: number
  y: number
}

interface Wall {
  start: Point
  end: Point
  thickness: number
  color: string
}

interface Viewer2DProps {
  className?: string
}

export const Viewer2D: React.FC<Viewer2DProps> = ({ className }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [scale, setScale] = useState(10) // pixels per unit
  const [offset, setOffset] = useState({ x: 0, y: 0 })
  const [isPanning, setIsPanning] = useState(false)
  const [lastPanPoint, setLastPanPoint] = useState<Point>({ x: 0, y: 0 })

  // Sample walls data
  const walls: Wall[] = [
    { start: { x: 0, y: 0 }, end: { x: 20, y: 0 }, thickness: 0.3, color: '#D3D3D3' },
    { start: { x: 20, y: 0 }, end: { x: 20, y: 30 }, thickness: 0.3, color: '#D3D3D3' },
    { start: { x: 20, y: 30 }, end: { x: 0, y: 30 }, thickness: 0.3, color: '#D3D3D3' },
    { start: { x: 0, y: 30 }, end: { x: 0, y: 0 }, thickness: 0.3, color: '#D3D3D3' },
  ]

  const drawGrid = (ctx: CanvasRenderingContext2D, width: number, height: number) => {
    ctx.strokeStyle = '#e0e0e0'
    ctx.lineWidth = 1

    // Major grid lines (10 units)
    ctx.strokeStyle = '#c0c0c0'
    for (let x = -100; x <= 100; x += 10) {
      const screenX = (x * scale) + offset.x + width / 2
      if (screenX >= 0 && screenX <= width) {
        ctx.beginPath()
        ctx.moveTo(screenX, 0)
        ctx.lineTo(screenX, height)
        ctx.stroke()
      }
    }

    for (let y = -100; y <= 100; y += 10) {
      const screenY = (y * scale) + offset.y + height / 2
      if (screenY >= 0 && screenY <= height) {
        ctx.beginPath()
        ctx.moveTo(0, screenY)
        ctx.lineTo(width, screenY)
        ctx.stroke()
      }
    }

    // Minor grid lines (1 unit)
    ctx.strokeStyle = '#f0f0f0'
    for (let x = -100; x <= 100; x += 1) {
      const screenX = (x * scale) + offset.x + width / 2
      if (screenX >= 0 && screenX <= width) {
        ctx.beginPath()
        ctx.moveTo(screenX, 0)
        ctx.lineTo(screenX, height)
        ctx.stroke()
      }
    }

    for (let y = -100; y <= 100; y += 1) {
      const screenY = (y * scale) + offset.y + height / 2
      if (screenY >= 0 && screenY <= height) {
        ctx.beginPath()
        ctx.moveTo(0, screenY)
        ctx.lineTo(width, screenY)
        ctx.stroke()
      }
    }
  }

  const drawWalls = (ctx: CanvasRenderingContext2D, width: number, height: number) => {
    walls.forEach(wall => {
      const startX = (wall.start.x * scale) + offset.x + width / 2
      const startY = (wall.start.y * scale) + offset.y + height / 2
      const endX = (wall.end.x * scale) + offset.x + width / 2
      const endY = (wall.end.y * scale) + offset.y + height / 2

      ctx.strokeStyle = wall.color
      ctx.lineWidth = wall.thickness * scale
      ctx.lineCap = 'round'

      ctx.beginPath()
      ctx.moveTo(startX, startY)
      ctx.lineTo(endX, endY)
      ctx.stroke()

      // Draw wall endpoints
      ctx.fillStyle = '#ff0000'
      ctx.beginPath()
      ctx.arc(startX, startY, 3, 0, 2 * Math.PI)
      ctx.fill()
      
      ctx.beginPath()
      ctx.arc(endX, endY, 3, 0, 2 * Math.PI)
      ctx.fill()
    })
  }

  const render = () => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const { width, height } = canvas

    // Clear canvas
    ctx.fillStyle = '#f8f9fa'
    ctx.fillRect(0, 0, width, height)

    // Draw grid
    drawGrid(ctx, width, height)

    // Draw coordinate axes
    ctx.strokeStyle = '#666'
    ctx.lineWidth = 2
    
    // X-axis
    ctx.beginPath()
    ctx.moveTo(0, height / 2 + offset.y)
    ctx.lineTo(width, height / 2 + offset.y)
    ctx.stroke()
    
    // Y-axis
    ctx.beginPath()
    ctx.moveTo(width / 2 + offset.x, 0)
    ctx.lineTo(width / 2 + offset.x, height)
    ctx.stroke()

    // Draw walls
    drawWalls(ctx, width, height)
  }

  useEffect(() => {
    render()
  }, [scale, offset])

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const resizeCanvas = () => {
      const parent = canvas.parentElement
      if (parent) {
        canvas.width = parent.clientWidth
        canvas.height = parent.clientHeight
        render()
      }
    }

    resizeCanvas()
    window.addEventListener('resize', resizeCanvas)

    return () => {
      window.removeEventListener('resize', resizeCanvas)
    }
  }, [])

  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault()
    const delta = e.deltaY > 0 ? 0.9 : 1.1
    setScale(prev => Math.max(1, Math.min(50, prev * delta)))
  }

  const handleMouseDown = (e: React.MouseEvent) => {
    setIsPanning(true)
    setLastPanPoint({ x: e.clientX, y: e.clientY })
  }

  const handleMouseMove = (e: React.MouseEvent) => {
    if (isPanning) {
      const deltaX = e.clientX - lastPanPoint.x
      const deltaY = e.clientY - lastPanPoint.y
      
      setOffset(prev => ({
        x: prev.x + deltaX,
        y: prev.y + deltaY
      }))
      
      setLastPanPoint({ x: e.clientX, y: e.clientY })
    }
  }

  const handleMouseUp = () => {
    setIsPanning(false)
  }

  return (
    <div className={`w-full h-full relative ${className}`}>
      <canvas
        ref={canvasRef}
        className="w-full h-full cursor-move"
        onWheel={handleWheel}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
      />
      
      {/* 2D View controls */}
      <div className="absolute top-4 left-4 bg-white rounded-lg shadow-lg p-2">
        <div className="text-sm font-medium mb-2">2D View</div>
        <div className="text-xs text-gray-600">
          Scale: {scale.toFixed(1)}x
        </div>
        <div className="text-xs text-gray-600 mt-1">
          Mouse: Pan | Wheel: Zoom
        </div>
      </div>
    </div>
  )
}