import { useMemo } from "react";
import { useGLTF } from "@react-three/drei";
import * as THREE from "three";
import { clone as cloneSkinned } from "three/examples/jsm/utils/SkeletonUtils.js";
import { applyShadows } from "@/shared/utils/shadows";
import { bottomAlignOffset, computeBbox, type BboxResult } from "@/shared/utils/glbHelpers";

interface UseGlbModelOptions {
  skinned?: boolean;
  castShadow?: boolean;
  receiveShadow?: boolean;
  overrideMap?: THREE.Texture | null;
}

export interface GlbModelResult {
  clone: THREE.Object3D;
  bbox: BboxResult;
  offset: THREE.Vector3; // bottom-align + x/z center
  animations: THREE.AnimationClip[];
}

// Scale is per-use-site — caller computes from bbox.size.
export function useGlbModel(url: string, opts: UseGlbModelOptions = {}): GlbModelResult {
  const { scene, animations } = useGLTF(url);
  const skinned = opts.skinned ?? false;
  const castShadow = opts.castShadow ?? true;
  const receiveShadow = opts.receiveShadow ?? true;
  const overrideMap = opts.overrideMap ?? null;

  return useMemo(() => {
    const clone = skinned ? cloneSkinned(scene) : scene.clone(true);
    applyShadows(clone, castShadow, receiveShadow);
    if (overrideMap) {
      clone.traverse((obj) => {
        const mesh = obj as THREE.Mesh;
        if (mesh.isMesh && mesh.material) {
          const mat = mesh.material as THREE.MeshStandardMaterial;
          if (mat.map) {
            mat.map = overrideMap;
            mat.needsUpdate = true;
          }
        }
      });
    }
    clone.updateMatrixWorld(true);
    const bbox = computeBbox(clone);
    const offset = bottomAlignOffset(bbox);
    return { clone, bbox, offset, animations };
  }, [scene, animations, skinned, castShadow, receiveShadow, overrideMap]);
}
