import { useSimulationMetricsStore } from "@/stores/simulationMetricsStore";

interface Props {
  minTime: number;
  maxTime: number;
}

export function PlaybackStatus({ minTime, maxTime }: Props) {
  const currentMinute = useSimulationMetricsStore((s) => s.currentMinute);
  const finished = useSimulationMetricsStore((s) => s.finished);
  const hasRange = maxTime > minTime;

  let label: string;
  let variant: "default" | "finished" = "default";
  if (!hasRange) {
    label = "No data";
  } else if (finished) {
    label = "end...";
    variant = "finished";
  } else if (currentMinute <= minTime) {
    label = "Ready to start…";
  } else {
    const pct = Math.round(((currentMinute - minTime) / (maxTime - minTime)) * 100);
    label = `Playing… (${pct}%)`;
  }

  return (
    <div className="px-3 py-2">
      <div
        className={`rounded-md border px-3 py-1.5 text-center text-xs font-medium ${
          variant === "finished"
            ? "border-primary/30 bg-primary/10 text-primary"
            : "bg-muted/40 text-muted-foreground"
        }`}
      >
        {label}
      </div>
    </div>
  );
}
