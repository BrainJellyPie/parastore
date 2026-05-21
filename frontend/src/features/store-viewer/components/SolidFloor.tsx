import { useMemo } from "react";
import { useLoader } from "@react-three/fiber";
import * as THREE from "three";

// Sample a single pale-lavender-grey pixel from Kenney colormap.png and apply it
// across the whole floor. UV coordinates pick the mid bottom-strip region to match
// the original Sample.png floor tone.
const FLOOR_UV: [number, number] = [0.54, 0.2];

interface SolidFloorProps {
  width: number;
  depth: number;
}

export function SolidFloor({ width, depth }: SolidFloorProps) {
  const tex = useLoader(THREE.TextureLoader, "/assets/market/Textures/colormap.png");
  tex.magFilter = THREE.NearestFilter;
  tex.minFilter = THREE.NearestFilter;
  tex.colorSpace = THREE.SRGBColorSpace;

  const geometry = useMemo(() => {
    const g = new THREE.PlaneGeometry(width, depth);
    const [u, v] = FLOOR_UV;
    const uvs = new Float32Array([u, v, u, v, u, v, u, v]);
    g.setAttribute("uv", new THREE.BufferAttribute(uvs, 2));
    return g;
  }, [width, depth]);

  return (
    <mesh
      position={[width / 2, 0, depth / 2]}
      rotation={[-Math.PI / 2, 0, 0]}
      receiveShadow
      geometry={geometry}
    >
      <meshStandardMaterial map={tex} roughness={0.9} />
    </mesh>
  );
}
