import { useSimulationMetricsStore } from "@/stores/simulationMetricsStore";

export function Summary() {
  const revenueCents = useSimulationMetricsStore((s) => s.revenue);
  const paidCount = useSimulationMetricsStore((s) => s.paidCount);
  const revenue = revenueCents / 100;
  const aov = paidCount > 0 ? revenue / paidCount : 0;

  return (
    <div className="border-t px-3 py-3">
      <div className="mb-2 text-xs font-medium">Summary</div>
      <div className="grid grid-cols-2 gap-3">
        <div>
          <div className="text-[11px] text-muted-foreground">Total revenue</div>
          <div className="mt-0.5 text-lg font-bold tabular-nums">
            ${revenue.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
        </div>
        <div>
          <div className="text-[11px] text-muted-foreground">Average order value</div>
          <div className="mt-0.5 text-lg font-bold tabular-nums">
            ${aov.toFixed(2)}
          </div>
        </div>
      </div>
    </div>
  );
}
