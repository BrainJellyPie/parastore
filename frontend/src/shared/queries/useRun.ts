import { useSuspenseQuery } from "@tanstack/react-query";
import * as api from "@/shared/api/client";
import type { Store, CustomerResult, Persona } from "@/shared/types/domain";
import type { RunSummary } from "@/shared/api/client";
import { queryKeys } from "./keys";
import { normalizeHeatmap } from "@/shared/utils/heatmap";

export interface RunBundle {
  runId: string;
  store: Store;
  personas: Persona[];
  customers: CustomerResult[];
  heatmap: number[][];
  summary: RunSummary;
}

// Run results are immutable — staleTime Infinity caches forever, gcTime drops it after 30min.
export function useRun(projectId: string, runId: string) {
  return useSuspenseQuery({
    queryKey: queryKeys.run(projectId, runId),
    queryFn: async ({ signal }): Promise<RunBundle> => {
      const [customers, summaryData, heatmapData, serverStore] = await Promise.all([
        api.getRunTimeline(projectId, runId, signal),
        api.getRunSummary(projectId, runId, signal),
        api.getRunHeatmap(projectId, runId, signal),
        api.getRunStore(projectId, runId, signal),
      ]);
      return {
        runId,
        store: serverStore,
        personas: Object.values(summaryData.personas),
        customers,
        heatmap: normalizeHeatmap(heatmapData.persona_heatmap),
        summary: summaryData.summary,
      };
    },
    staleTime: Infinity,
    gcTime: 1000 * 60 * 30,
  });
}
