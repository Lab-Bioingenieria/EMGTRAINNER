import { Suspense, useState, useEffect } from 'react'
import { Canvas } from '@react-three/fiber'
import { OrbitControls, Environment, ContactShadows, PerspectiveCamera } from '@react-three/drei'
import { Card } from './ui/card'
import { Badge } from './ui/badge'
import { ProstheticModel } from './prosthetic-3d-model'

interface ProstheticViewerProps {
  isActive?: boolean
}

export function ProstheticViewer({ isActive = false }: ProstheticViewerProps) {
  const [fingerRotation, setFingerRotation] = useState(0)
  const [wristRotation, setWristRotation] = useState(0)
  const [elbowRotation, setElbowRotation] = useState(0)
  const [isConnected, setIsConnected] = useState(false)

  // Simulate connection after mount
  useEffect(() => {
    const timer = setTimeout(() => setIsConnected(true), 1000)
    return () => clearTimeout(timer)
  }, [])

  // Simulate real-time data updates
  useEffect(() => {
    if (!isConnected || !isActive) return

    const interval = setInterval(() => {
      // Simulate EMG signal affecting finger movement
      setFingerRotation((prev) => {
        const target = Math.sin(Date.now() / 1000) * 0.5
        return prev + (target - prev) * 0.1
      })
      
      setWristRotation((prev) => {
        const target = Math.cos(Date.now() / 1500) * 0.3
        return prev + (target - prev) * 0.1
      })

      setElbowRotation((prev) => {
        const target = Math.sin(Date.now() / 2000) * 0.2
        return prev + (target - prev) * 0.1
      })
    }, 50)

    return () => clearInterval(interval)
  }, [isConnected, isActive])

  return (
    <Card className="relative h-full min-h-[500px] overflow-hidden bg-gradient-to-br from-background via-muted/20 to-background">
      {/* Grid background effect */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px]" />
      
      {/* 3D Canvas */}
      <div className="relative z-10 h-full w-full">
        <Canvas shadows>
          <PerspectiveCamera makeDefault position={[3, 2, 4]} fov={50} />
          
          {/* Lighting */}
          <ambientLight intensity={0.4} />
          <spotLight
            position={[10, 10, 10]}
            angle={0.15}
            penumbra={1}
            intensity={1}
            castShadow
            shadow-mapSize={[2048, 2048]}
          />
          <pointLight position={[-10, -10, -10]} intensity={0.5} color="#0ea5e9" />
          
          {/* 3D Model */}
          <Suspense fallback={null}>
            <ProstheticModel 
              fingerRotation={fingerRotation}
              wristRotation={wristRotation}
              elbowRotation={elbowRotation}
            />
            <ContactShadows
              position={[0, -2, 0]}
              opacity={0.4}
              scale={10}
              blur={2}
              far={4}
            />
            <Environment preset="city" />
          </Suspense>

          {/* Camera Controls */}
          <OrbitControls
            enablePan={false}
            enableZoom={true}
            minDistance={2}
            maxDistance={8}
            minPolarAngle={Math.PI / 4}
            maxPolarAngle={Math.PI / 2}
          />
        </Canvas>
      </div>

      {/* UI Overlays */}
      <div className="absolute top-4 left-4 flex items-center gap-2">
        <div className={`size-2 rounded-full ${isConnected ? 'animate-pulse bg-chart-1' : 'bg-muted-foreground'}`} />
        <span className="text-xs text-muted-foreground">
          {isConnected ? 'Live View' : 'Connecting...'}
        </span>
      </div>
      
      <div className="absolute top-4 right-4 flex flex-col items-end gap-1">
        <span className="text-xs text-muted-foreground">FPS: 60</span>
        <Badge variant="outline" className="border-primary/50 bg-primary/10 text-primary">
          {isActive && isConnected ? 'Active' : 'Standby'}
        </Badge>
      </div>

      {/* Joint Angles Display */}
      <div className="absolute bottom-4 left-4 flex flex-col gap-1 rounded-lg border border-border/50 bg-background/80 p-3 backdrop-blur-sm">
        <div className="text-xs font-medium">Joint Angles</div>
        <div className="flex flex-col gap-0.5 text-xs text-muted-foreground">
          <div>Elbow: {(elbowRotation * (180 / Math.PI)).toFixed(1)}°</div>
          <div>Wrist: {(wristRotation * (180 / Math.PI)).toFixed(1)}°</div>
          <div>Fingers: {(fingerRotation * (180 / Math.PI)).toFixed(1)}°</div>
        </div>
      </div>
    </Card>
  )
}
