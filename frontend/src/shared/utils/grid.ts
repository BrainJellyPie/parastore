import type { Face, Rack } from "../types/domain";

export const LEVEL_HEIGHT = 0.5;

export function rackWorldCenter(rack: Rack): [number, number, number] {
  const { w, d } = rackBounds(rack);
  const [gx, gz] = rack.position;
  return [gx + w / 2, 0, gz + d / 2];
}

export const TYPE_COLORS: Record<string, string> = {
  shelf: "#8B6914",
  fridge: "#4682B4",
  counter: "#DAA520",
  display: "#FF69B4",
  table: "#9370DB",
  wall: "#808080",
  entrance: "#32CD32",
  exit: "#FF6347",
};

export function rackBounds(rack: Rack): { w: number; d: number } {
  const rows = rack.shape.length;
  const cols = rack.shape[0]?.length ?? 0;
  if (rack.rotation === 90 || rack.rotation === 270) {
    return { w: rows, d: cols };
  }
  return { w: cols, d: rows };
}

export function rackHeight(rack: Rack): number {
  return Math.max(rack.levels, 1) * LEVEL_HEIGHT;
}

export function facesWithProducts(rack: Rack): Set<Face> {
  const set = new Set<Face>();
  for (const s of rack.slots) set.add(s.face);
  return set;
}

