/**
 * 3D Viewer component using React Three Fiber
 */

'use client'

import React, { useRef, useState } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, Grid, Box, Plane } from '@react-three/drei'
import * as THREE from 'three'

interface Building3DProps {
  position?: [number, number, number]
  color?: string
}

const Building3D: React.FC<Building3DProps> = ({ position = [0, 0, 0], color = '#8B4513' }) => {
  const meshRef = useRef<THREE.Mesh>(null!)
  const [hovered, setHovered] = useState(false)

  useFrame((state, delta) => {
    if (meshRef.current && hovered) {
      meshRef.current.rotation.y += delta * 0.5
    }
  })

  return (
    <Box
      ref={meshRef}
      position={position}
      args={[20, 15, 30]}
      onPointerOver={() => setHovered(true)}
      onPointerOut={() => setHovered(false)}
    >
      <meshStandardMaterial color={hovered ? '#A0522D' : color} />
    </Box>
  )
}

interface Wall3DProps {
  start: [number, number, number]
  end: [number, number, number]
  height: number
  thickness: number
  color?: string
}

const Wall3D: React.FC<Wall3DProps> = ({ start, end, height, thickness, color = '#D3D3D3' }) => {
  const length = Math.sqrt(
    Math.pow(end[0] - start[0], 2) + 
    Math.pow(end[1] - start[1], 2) + 
    Math.pow(end[2] - start[2], 2)
  )
  
  const midPoint: [number, number, number] = [
    (start[0] + end[0]) / 2,
    height / 2,
    (start[1] + end[1]) / 2
  ]
  
  const angle = Math.atan2(end[1] - start[1], end[0] - start[0])

  return (
    <Box
      position={midPoint}
      args={[length, height, thickness]}
      rotation={[0, angle, 0]}
    >
      <meshStandardMaterial color={color} />
    </Box>
  )
}

interface Viewer3DProps {
  className?: string
}

export const Viewer3D: React.FC<Viewer3DProps> = ({ className }) => {
  return (
    <div className={`w-full h-full ${className}`}>
      <Canvas
        camera={{ position: [50, 30, 50], fov: 60 }}
        shadows
        style={{ background: '#f0f8ff' }}
      >
        {/* Lighting */}
        <ambientLight intensity={0.4} />
        <directionalLight
          position={[10, 10, 5]}
          intensity={1}
          castShadow
          shadow-mapSize-width={2048}
          shadow-mapSize-height={2048}
        />
        
        {/* Ground grid */}
        <Grid 
          position={[0, -0.1, 0]} 
          args={[100, 100]} 
          cellSize={1} 
          cellThickness={0.5} 
          cellColor="#d0d0d0" 
          sectionSize={10} 
          sectionThickness={1} 
          sectionColor="#808080" 
        />
        
        {/* Ground plane */}
        <Plane
          position={[0, -0.2, 0]}
          rotation={[-Math.PI / 2, 0, 0]}
          args={[200, 200]}
          receiveShadow
        >
          <meshStandardMaterial color="#e8f4f8" />
        </Plane>
        
        {/* Sample building */}
        <Building3D position={[0, 7.5, 0]} />
        
        {/* Sample walls */}
        <Wall3D start={[0, 0, 0]} end={[20, 0, 0]} height={15} thickness={0.3} />
        <Wall3D start={[20, 0, 0]} end={[20, 0, 30]} height={15} thickness={0.3} />
        <Wall3D start={[20, 0, 30]} end={[0, 0, 30]} height={15} thickness={0.3} />
        <Wall3D start={[0, 0, 30]} end={[0, 0, 0]} height={15} thickness={0.3} />
        
        {/* Controls */}
        <OrbitControls
          enablePan={true}
          enableZoom={true}
          enableRotate={true}
          minPolarAngle={0}
          maxPolarAngle={Math.PI / 2}
        />
      </Canvas>
    </div>
  )
}