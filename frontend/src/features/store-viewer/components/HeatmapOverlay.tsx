import { useMemo } from "react";
import * as THREE from "three";

export type HeatmapMode = "off" | "predicted" | "simulated";

interface HeatmapOverlayProps {
  data: number[][];
  mode: "predicted" | "simulated";
  width: number;
  depth: number;
}

export function HeatmapOverlay({ data, mode, width, depth }: HeatmapOverlayProps) {
  const [r, g, b] = mode === "predicted" ? [255, 120, 40] : [40, 130, 220];

  const texture = useMemo(() => {
    const pixels = new Uint8Array(width * depth * 4);
    for (let y = 0; y < depth; y++) {
      for (let x = 0; x < width; x++) {
        const v = Math.max(0, Math.min(1, data[y]?.[x] ?? 0));
        const py = depth - 1 - y;
        const i = (py * width + x) * 4;
        pixels[i] = r;
        pixels[i + 1] = g;
        pixels[i + 2] = b;
        pixels[i + 3] = Math.round(v * 180);
      }
    }
    const tex = new THREE.DataTexture(pixels, width, depth, THREE.RGBAFormat);
    tex.magFilter = THREE.LinearFilter;
    tex.minFilter = THREE.LinearFilter;
    tex.needsUpdate = true;
    return tex;
  }, [data, width, depth, r, g, b]);

  return (
    <mesh position={[width / 2, 0.05, depth / 2]} rotation={[-Math.PI / 2, 0, 0]}>
      <planeGeometry args={[width, depth]} />
      <meshBasicMaterial map={texture} transparent depthWrite={false} />
    </mesh>
  );
}
