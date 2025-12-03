import { useRef, useState } from 'react'
import { useFrame } from '@react-three/fiber'
import { Mesh } from 'three'

interface ProstheticModelProps {
  fingerRotation?: number
  wristRotation?: number
  elbowRotation?: number
}

export function ProstheticModel({ 
  fingerRotation = 0, 
  wristRotation = 0,
  elbowRotation = 0 
}: ProstheticModelProps) {
  const upperArmRef = useRef<Mesh>(null)
  const forearmRef = useRef<Mesh>(null)
  const handRef = useRef<Mesh>(null)
  const finger1Ref = useRef<Mesh>(null)
  const finger2Ref = useRef<Mesh>(null)
  const finger3Ref = useRef<Mesh>(null)
  const thumbRef = useRef<Mesh>(null)
  const [hovered, setHovered] = useState(false)

  // Subtle idle animation
  useFrame((state) => {
    const time = state.clock.getElapsedTime()
    if (upperArmRef.current && !hovered) {
      upperArmRef.current.rotation.y = Math.sin(time * 0.3) * 0.1
    }
  })

  return (
    <group 
      position={[0, 0, 0]}
      onPointerOver={() => setHovered(true)}
      onPointerOut={() => setHovered(false)}
    >
      {/* Upper Arm */}
      <mesh ref={upperArmRef} position={[0, 1.5, 0]} castShadow>
        <cylinderGeometry args={[0.15, 0.12, 1.5, 16]} />
        <meshStandardMaterial 
          color="#1e293b" 
          metalness={0.8} 
          roughness={0.2}
        />
      </mesh>

      {/* Elbow Joint */}
      <mesh position={[0, 0.75, 0]} castShadow>
        <sphereGeometry args={[0.18, 16, 16]} />
        <meshStandardMaterial 
          color="#0ea5e9" 
          metalness={0.9} 
          roughness={0.1}
          emissive="#0ea5e9"
          emissiveIntensity={0.2}
        />
      </mesh>

      {/* Forearm */}
      <group rotation={[elbowRotation, 0, 0]}>
        <mesh ref={forearmRef} position={[0, 0, 0]} castShadow>
          <cylinderGeometry args={[0.12, 0.1, 1.5, 16]} />
          <meshStandardMaterial 
            color="#1e293b" 
            metalness={0.8} 
            roughness={0.2}
          />
        </mesh>

        {/* Wrist Joint */}
        <mesh position={[0, -0.75, 0]} castShadow>
          <sphereGeometry args={[0.15, 16, 16]} />
          <meshStandardMaterial 
            color="#0ea5e9" 
            metalness={0.9} 
            roughness={0.1}
            emissive="#0ea5e9"
            emissiveIntensity={0.2}
          />
        </mesh>

        {/* Hand */}
        <group position={[0, -1.2, 0]} rotation={[0, wristRotation, 0]}>
          <mesh ref={handRef} castShadow>
            <boxGeometry args={[0.4, 0.6, 0.15]} />
            <meshStandardMaterial 
              color="#1e293b" 
              metalness={0.8} 
              roughness={0.2}
            />
          </mesh>

          {/* Thumb */}
          <group position={[-0.25, 0.1, 0]} rotation={[0, 0, -fingerRotation * 0.8]}>
            <mesh ref={thumbRef} position={[-0.15, 0, 0]} castShadow>
              <boxGeometry args={[0.3, 0.08, 0.08]} />
              <meshStandardMaterial 
                color="#334155" 
                metalness={0.7} 
                roughness={0.3}
              />
            </mesh>
            <mesh position={[-0.25, 0, 0]} castShadow>
              <sphereGeometry args={[0.06, 12, 12]} />
              <meshStandardMaterial 
                color="#0ea5e9" 
                metalness={0.9} 
                roughness={0.1}
                emissive="#0ea5e9"
                emissiveIntensity={0.3}
              />
            </mesh>
          </group>

          {/* Index Finger */}
          <group position={[-0.12, 0.35, 0]} rotation={[fingerRotation, 0, 0]}>
            <mesh ref={finger1Ref} position={[0, 0.2, 0]} castShadow>
              <boxGeometry args={[0.08, 0.4, 0.08]} />
              <meshStandardMaterial 
                color="#334155" 
                metalness={0.7} 
                roughness={0.3}
              />
            </mesh>
            <mesh position={[0, 0.35, 0]} castShadow>
              <sphereGeometry args={[0.05, 12, 12]} />
              <meshStandardMaterial 
                color="#0ea5e9" 
                metalness={0.9} 
                roughness={0.1}
                emissive="#0ea5e9"
                emissiveIntensity={0.3}
              />
            </mesh>
          </group>

          {/* Middle Finger */}
          <group position={[0, 0.35, 0]} rotation={[fingerRotation, 0, 0]}>
            <mesh ref={finger2Ref} position={[0, 0.25, 0]} castShadow>
              <boxGeometry args={[0.08, 0.5, 0.08]} />
              <meshStandardMaterial 
                color="#334155" 
                metalness={0.7} 
                roughness={0.3}
              />
            </mesh>
            <mesh position={[0, 0.45, 0]} castShadow>
              <sphereGeometry args={[0.05, 12, 12]} />
              <meshStandardMaterial 
                color="#0ea5e9" 
                metalness={0.9} 
                roughness={0.1}
                emissive="#0ea5e9"
                emissiveIntensity={0.3}
              />
            </mesh>
          </group>

          {/* Ring Finger */}
          <group position={[0.12, 0.35, 0]} rotation={[fingerRotation, 0, 0]}>
            <mesh ref={finger3Ref} position={[0, 0.2, 0]} castShadow>
              <boxGeometry args={[0.08, 0.4, 0.08]} />
              <meshStandardMaterial 
                color="#334155" 
                metalness={0.7} 
                roughness={0.3}
              />
            </mesh>
            <mesh position={[0, 0.35, 0]} castShadow>
              <sphereGeometry args={[0.05, 12, 12]} />
              <meshStandardMaterial 
                color="#0ea5e9" 
                metalness={0.9} 
                roughness={0.1}
                emissive="#0ea5e9"
                emissiveIntensity={0.3}
              />
            </mesh>
          </group>
        </group>
      </group>
    </group>
  )
}

