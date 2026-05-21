import type { Face } from "@/shared/types/domain";

const EXCEL_TO_DOMAIN: Record<string, Face> = {
  north: "N", south: "S", east: "E", west: "W",
  n: "N", s: "S", e: "E", w: "W",
};

const DOMAIN_TO_EXCEL: Record<Face, string> = {
  N: "North", S: "South", E: "East", W: "West",
};

export function parseFace(raw: string): Face {
  const key = raw.trim().toLowerCase();
  const face = EXCEL_TO_DOMAIN[key];
  if (!face) throw new Error(`Unknown face value: ${raw}`);
  return face;
}

export function formatFace(face: Face): string {
  return DOMAIN_TO_EXCEL[face];
}
