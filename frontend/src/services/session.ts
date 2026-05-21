import * as api from "@/shared/api/client";
import { abortableDelay } from "@/shared/utils/abortableDelay";
import { normalizeHeatmap } from "@/shared/utils/heatmap";
import type { RunBundle } from "@/shared/queries/useRun";

const POLL_INTERVAL = 2000;

async function pollUntilComplete(
  projectId: string,
  runId: string,
  signal?: AbortSignal,
): Promise<void> {
  while (!signal?.aborted) {
    const status = await api.getRunStatus(projectId, runId, signal);
    if (signal?.aborted) return;
    if (status.status === "completed") return;
    if (status.status === "failed") {
      throw new Error(status.error || "Simulation failed");
    }
    await abortableDelay(POLL_INTERVAL, signal);
  }
}

async function fetchRunData(
  projectId: string,
  runId: string,
  signal?: AbortSignal,
): Promise<RunBundle> {
  const [customers, summaryData, heatmapData, serverStore] = await Promise.all([
    api.getRunTimeline(projectId, runId, signal),
    api.getRunSummary(projectId, runId, signal),
    api.getRunHeatmap(projectId, runId, signal),
    api.getRunStore(projectId, runId, signal),
  ]);
  return {
    runId,
    customers,
    heatmap: normalizeHeatmap(heatmapData.persona_heatmap),
    summary: summaryData.summary,
    store: serverStore,
    personas: Object.values(summaryData.personas),
  };
}

export async function simulateSession(
  projectId: string,
  setupId: string,
  signal?: AbortSignal,
): Promise<RunBundle> {
  const { run_id } = await api.startRun(projectId, setupId, signal);
  await pollUntilComplete(projectId, run_id, signal);
  return fetchRunData(projectId, run_id, signal);
}
