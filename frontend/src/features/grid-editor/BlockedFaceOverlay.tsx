// Cell-edge stripes that visualize blocked faces of a single rack.
//
// 4-edge stripes: N (top), S (bottom), W (left), E (right). One stripe per face,
// with color picked from the highest-priority reason listed for that face.
// Priority: unreachable > occluded > out_of_bounds > locked > occupied.

import type { BlockedFaceDetail, BlockReason, Face } from "@/shared/types/domain";
import { cn } from "@/shared/utils/cn";

interface BlockedFaceOverlayProps {
  blockedFaces: BlockedFaceDetail[]; // for a single rack only
}

const REASON_PRIORITY: BlockReason[] = [
  "unreachable",
  "occluded",
  "out_of_bounds",
  "locked",
  "occupied",
];

const REASON_COLOR: Record<BlockReason, string> = {
  occluded: "bg-zinc-400",
  out_of_bounds: "bg-zinc-900",
  unreachable: "bg-red-500",
  locked: "bg-orange-500",
  occupied: "bg-purple-500",
};

const EDGE_POSITION: Record<Face, string> = {
  N: "absolute inset-x-0 top-0 h-0.5",
  S: "absolute inset-x-0 bottom-0 h-0.5",
  W: "absolute inset-y-0 left-0 w-0.5",
  E: "absolute inset-y-0 right-0 w-0.5",
};

function pickReason(reasons: BlockReason[]): BlockReason | null {
  for (const r of REASON_PRIORITY) {
    if (reasons.includes(r)) return r;
  }
  return null;
}

export function BlockedFaceOverlay({ blockedFaces }: BlockedFaceOverlayProps) {
  // Merge reasons per face across multiple entries (one rack may have several
  // BlockedFaceDetail rows for the same face if upstream merging didn't run).
  const byFace = new Map<Face, BlockReason[]>();
  for (const detail of blockedFaces) {
    const existing = byFace.get(detail.face) ?? [];
    byFace.set(detail.face, [...existing, ...detail.reasons]);
  }

  const stripes: Array<{ face: Face; reason: BlockReason }> = [];
  for (const [face, reasons] of byFace) {
    const reason = pickReason(reasons);
    if (reason) stripes.push({ face, reason });
  }

  if (stripes.length === 0) return null;

  return (
    <>
      {stripes.map(({ face, reason }) => (
        <div
          key={face}
          data-testid={`blocked-stripe-${face}`}
          data-face={face}
          data-reason={reason}
          className={cn(EDGE_POSITION[face], REASON_COLOR[reason], "pointer-events-none")}
        />
      ))}
    </>
  );
}
