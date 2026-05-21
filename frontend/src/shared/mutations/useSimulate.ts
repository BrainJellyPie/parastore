import { useMutation, useQueryClient } from "@tanstack/react-query";
import { simulateSession } from "@/services/session";
import { queryKeys } from "@/shared/queries/keys";
import type { RunBundle } from "@/shared/queries/useRun";

interface SimulateArgs {
  projectId: string;
  setupId: string;
}

export function useSimulate() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ projectId, setupId }: SimulateArgs) =>
      simulateSession(projectId, setupId),
    onSuccess: (run, { projectId, setupId }) => {
      qc.invalidateQueries({ queryKey: queryKeys.runs(projectId, setupId) });
      qc.setQueryData<RunBundle>(queryKeys.run(projectId, run.runId), run);
    },
  });
}
