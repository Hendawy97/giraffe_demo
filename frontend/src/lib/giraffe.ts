/**
 * Giraffe SDK integration and utilities
 */

export interface GiraffeConfig {
  container: string | HTMLElement
  apiUrl?: string
  token?: string
  mode?: '2d' | '3d'
  enableControls?: boolean
  enableMiniMap?: boolean
  theme?: 'light' | 'dark'
}

export interface GiraffeViewer {
  // Core methods
  loadProject(projectId: string): Promise<void>
  setMode(mode: '2d' | '3d'): void
  destroy(): void
  
  // Camera controls
  zoomIn(): void
  zoomOut(): void
  resetView(): void
  fitToView(): void
  
  // Object manipulation
  selectObject(objectId: string): void
  deselectAll(): void
  
  // Event handling
  on(event: string, callback: Function): void
  off(event: string, callback: Function): void
  
  // Tools
  setTool(tool: string): void
  addWall(options: WallOptions): Promise<string>
  addDoor(options: DoorOptions): Promise<string>
  updateObject(objectId: string, properties: any): Promise<void>
  deleteObject(objectId: string): Promise<void>
}

export interface WallOptions {
  start: [number, number, number]
  end: [number, number, number]
  height: number
  thickness?: number
  material?: string
  color?: string
}

export interface DoorOptions {
  position: [number, number, number]
  width: number
  height: number
  wallId?: string
  type?: 'single' | 'double' | 'sliding'
}

// Global Giraffe object (loaded from CDN or external script)
declare global {
  interface Window {
    Giraffe?: {
      Viewer: new (config: GiraffeConfig) => GiraffeViewer
      version: string
      isLoaded: boolean
    }
  }
}

/**
 * Initialize Giraffe SDK
 */
export const initializeGiraffe = (): Promise<void> => {
  return new Promise((resolve, reject) => {
    // Check if already loaded
    if (window.Giraffe?.isLoaded) {
      resolve()
      return
    }

    // For demo purposes, we'll simulate the SDK
    // In real implementation, this would load the actual Giraffe SDK
    if (typeof window !== 'undefined') {
      // Simulate loading the Giraffe SDK
      setTimeout(() => {
        window.Giraffe = {
          Viewer: MockGiraffeViewer as any,
          version: '1.0.0-demo',
          isLoaded: true,
        }
        resolve()
      }, 1000)
    } else {
      reject(new Error('Window object not available'))
    }
  })
}

/**
 * Mock Giraffe Viewer for demo purposes
 * In real implementation, this would be the actual Giraffe SDK
 */
class MockGiraffeViewer implements GiraffeViewer {
  private container: HTMLElement
  private mode: '2d' | '3d' = '3d'
  private canvas: HTMLCanvasElement
  private ctx: CanvasRenderingContext2D | null = null
  private eventListeners: { [key: string]: Function[] } = {}

  constructor(config: GiraffeConfig) {
    this.container = typeof config.container === 'string' 
      ? document.getElementById(config.container)! 
      : config.container

    if (!this.container) {
      throw new Error('Container not found')
    }

    this.mode = config.mode || '3d'
    this.initializeCanvas()
    this.render()
  }

  private initializeCanvas() {
    this.canvas = document.createElement('canvas')
    this.canvas.style.width = '100%'
    this.canvas.style.height = '100%'
    this.canvas.style.display = 'block'
    
    this.container.innerHTML = ''
    this.container.appendChild(this.canvas)
    
    this.ctx = this.canvas.getContext('2d')
    this.resizeCanvas()
    
    // Handle resize
    window.addEventListener('resize', () => this.resizeCanvas())
    
    // Handle mouse events
    this.canvas.addEventListener('click', (e) => {
      this.emit('click', { x: e.offsetX, y: e.offsetY })
    })
  }

  private resizeCanvas() {
    const rect = this.container.getBoundingClientRect()
    this.canvas.width = rect.width
    this.canvas.height = rect.height
    this.render()
  }

  private render() {
    if (!this.ctx) return

    const { width, height } = this.canvas
    
    // Clear canvas
    this.ctx.fillStyle = this.mode === '3d' ? '#f0f8ff' : '#f8f9fa'
    this.ctx.fillRect(0, 0, width, height)
    
    if (this.mode === '3d') {
      this.render3D()
    } else {
      this.render2D()
    }
  }

  private render3D() {
    if (!this.ctx) return
    
    const { width, height } = this.canvas
    
    // Draw a simple 3D-style building
    this.ctx.fillStyle = '#8B4513'
    this.ctx.fillRect(width/2 - 50, height/2 - 30, 100, 60)
    
    // Add some 3D effect
    this.ctx.fillStyle = '#654321'
    this.ctx.fillRect(width/2 + 50, height/2 - 30, 20, 60)
    this.ctx.fillRect(width/2 - 50, height/2 - 50, 100, 20)
    
    // Add Giraffe SDK branding
    this.ctx.fillStyle = '#333'
    this.ctx.font = '16px Arial'
    this.ctx.textAlign = 'center'
    this.ctx.fillText('Giraffe SDK - 3D View', width/2, 30)
    this.ctx.fillText('Demo Building Model', width/2, height - 30)
  }

  private render2D() {
    if (!this.ctx) return
    
    const { width, height } = this.canvas
    
    // Draw grid
    this.ctx.strokeStyle = '#e0e0e0'
    this.ctx.lineWidth = 1
    
    for (let x = 0; x < width; x += 20) {
      this.ctx.beginPath()
      this.ctx.moveTo(x, 0)
      this.ctx.lineTo(x, height)
      this.ctx.stroke()
    }
    
    for (let y = 0; y < height; y += 20) {
      this.ctx.beginPath()
      this.ctx.moveTo(0, y)
      this.ctx.lineTo(width, y)
      this.ctx.stroke()
    }
    
    // Draw walls
    this.ctx.strokeStyle = '#D3D3D3'
    this.ctx.lineWidth = 3
    
    const centerX = width / 2
    const centerY = height / 2
    
    // Rectangle floor plan
    this.ctx.strokeRect(centerX - 60, centerY - 40, 120, 80)
    
    // Add Giraffe SDK branding
    this.ctx.fillStyle = '#333'
    this.ctx.font = '16px Arial'
    this.ctx.textAlign = 'center'
    this.ctx.fillText('Giraffe SDK - 2D View', width/2, 30)
    this.ctx.fillText('Floor Plan View', width/2, height - 30)
  }

  async loadProject(projectId: string): Promise<void> {
    console.log(`Loading project: ${projectId}`)
    // Simulate loading delay
    await new Promise(resolve => setTimeout(resolve, 500))
    this.render()
    this.emit('projectLoaded', { projectId })
  }

  setMode(mode: '2d' | '3d'): void {
    this.mode = mode
    this.render()
    this.emit('modeChanged', { mode })
  }

  zoomIn(): void {
    console.log('Zoom in')
    this.emit('zoom', { direction: 'in' })
  }

  zoomOut(): void {
    console.log('Zoom out')
    this.emit('zoom', { direction: 'out' })
  }

  resetView(): void {
    console.log('Reset view')
    this.render()
    this.emit('viewReset')
  }

  fitToView(): void {
    console.log('Fit to view')
    this.render()
    this.emit('fitToView')
  }

  selectObject(objectId: string): void {
    console.log(`Select object: ${objectId}`)
    this.emit('objectSelected', { objectId })
  }

  deselectAll(): void {
    console.log('Deselect all')
    this.emit('selectionCleared')
  }

  setTool(tool: string): void {
    console.log(`Set tool: ${tool}`)
    this.emit('toolChanged', { tool })
  }

  async addWall(options: WallOptions): Promise<string> {
    console.log('Add wall:', options)
    const wallId = `wall_${Date.now()}`
    this.emit('objectAdded', { type: 'wall', id: wallId, options })
    return wallId
  }

  async addDoor(options: DoorOptions): Promise<string> {
    console.log('Add door:', options)
    const doorId = `door_${Date.now()}`
    this.emit('objectAdded', { type: 'door', id: doorId, options })
    return doorId
  }

  async updateObject(objectId: string, properties: any): Promise<void> {
    console.log(`Update object ${objectId}:`, properties)
    this.emit('objectUpdated', { objectId, properties })
  }

  async deleteObject(objectId: string): Promise<void> {
    console.log(`Delete object: ${objectId}`)
    this.emit('objectDeleted', { objectId })
  }

  on(event: string, callback: Function): void {
    if (!this.eventListeners[event]) {
      this.eventListeners[event] = []
    }
    this.eventListeners[event].push(callback)
  }

  off(event: string, callback: Function): void {
    if (this.eventListeners[event]) {
      this.eventListeners[event] = this.eventListeners[event].filter(cb => cb !== callback)
    }
  }

  private emit(event: string, data?: any): void {
    if (this.eventListeners[event]) {
      this.eventListeners[event].forEach(callback => callback(data))
    }
  }

  destroy(): void {
    this.container.innerHTML = ''
    this.eventListeners = {}
    window.removeEventListener('resize', () => this.resizeCanvas())
  }
}