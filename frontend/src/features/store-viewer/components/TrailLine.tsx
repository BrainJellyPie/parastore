import { Line } from "@react-three/drei";

interface TrailLineProps {
  trail: { x: number; y: number }[];
  color: string;
  dimmed?: boolean;
  emphasized?: boolean;
}

export function TrailLine({ trail, color, dimmed, emphasized }: TrailLineProps) {
  if (trail.length < 2) return null;
  const points = trail.map((p) => [p.x + 0.5, 0.08, p.y + 0.5] as [number, number, number]);
  return (
    <Line
      points={points}
      color={color}
      lineWidth={emphasized ? 4 : 2.75}
      transparent
      opacity={dimmed ? 0.14 : emphasized ? 0.82 : 0.52}
    />
  );
}
