import * as THREE from "three";

export interface BboxResult {
  box: THREE.Box3;
  size: THREE.Vector3;
  center: THREE.Vector3;
}

// Caller must call updateMatrixWorld first or the AABB will be stale.
export function computeBbox(obj: THREE.Object3D): BboxResult {
  const box = new THREE.Box3().setFromObject(obj);
  const size = new THREE.Vector3();
  const center = new THREE.Vector3();
  box.getSize(size);
  box.getCenter(center);
  return { box, size, center };
}

export function bottomAlignOffset(bbox: BboxResult): THREE.Vector3 {
  return new THREE.Vector3(-bbox.center.x, -bbox.box.min.y, -bbox.center.z);
}

export function uniformScaleToTile(bbox: BboxResult): number {
  return 1 / (Math.max(bbox.size.x, bbox.size.z) || 1);
}
