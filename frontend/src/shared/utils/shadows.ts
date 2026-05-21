import * as THREE from "three";

export function applyShadows(root: THREE.Object3D, cast: boolean, receive: boolean) {
  root.traverse((obj) => {
    if ((obj as THREE.Mesh).isMesh) {
      obj.castShadow = cast;
      obj.receiveShadow = receive;
    }
  });
}
