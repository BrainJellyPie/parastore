import { useSuspenseQuery } from "@tanstack/react-query";
import * as api from "@/shared/api/client";
import { queryKeys } from "./keys";

export function useRuns(projectId: string, setupId: string) {
  return useSuspenseQuery({
    queryKey: queryKeys.runs(projectId, setupId),
    queryFn: ({ signal }) => api.getRuns(projectId, setupId, signal),
  });
}
